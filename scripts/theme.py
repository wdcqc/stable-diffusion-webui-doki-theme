from modules import script_callbacks
import modules.scripts as scripts
import gradio as gr
import os, json, re, shutil

from dokithemejupyter.themes import themes
import cv2, numpy as np
from PIL import ImageColor

self_dir = scripts.basedir()

def to_rgba(color, opacity):
    """
    Converts color to CSS RGBA format.

    @param color {str} CSS color of any kind.
    @param opacity {float} Target opacity of the color.
    @returns {str} CSS color of RGBA format.
    """
    rgb = ImageColor.getcolor(color, "RGB")
    return "rgba({}, {}, {}, {})".format(*rgb, opacity)

def change_lumi(color, delta):
    """
    Modifies the luminance of a color by converting it to LAB and back.

    @param color {str} CSS color of any kind.
    @param delta {int} Increment of luminance, range from -255 to 255.
    @returns {str} CSS color of RGB format.
    """
    if isinstance(color, str):
        rgb = ImageColor.getcolor(color, "RGB")
    else:
        rgb = color
        
    lab = cv2.cvtColor(np.array([[rgb]], dtype=np.uint8), cv2.COLOR_RGB2LAB)
    lab[0, 0, 0] = min(255, max(0, int(lab[0, 0, 0]) + delta))
    rgb_arr = cv2.cvtColor(lab, cv2.COLOR_LAB2RGB)
    rgb = rgb_arr[0, 0]
    
    return "rgb({}, {}, {})".format(*rgb)

def generate_gradio_css(tempura, theme_color):
    """
    Generates the CSS declaration of the Doki Theme for the Gradio app.

    @param tempura {str} Format string containing parameters nicely contained in curly braces.
    @param theme_color {dict} Dictionary containing every color using Doki definition.
    @returns {str} Expressively generated CSS stylesheet.
    """
    css = tempura.format(
        shadowColor = theme_color["selectionBackground"],
        shadowColorTransparent = to_rgba(theme_color["selectionBackground"], 0.7),
        accentShadowColor = to_rgba(theme_color["accentColor"], 0.7),
        accentColorReallyTransparent = to_rgba(theme_color["accentColor"], 0.3),
        accentColorDeeper = change_lumi(theme_color["accentColor"], -25),
        gradientFrom = theme_color["baseBackground"],
        gradientTo = change_lumi(theme_color["baseBackground"], 25),
        secondaryGradientFrom = theme_color["secondaryBackground"],
        secondaryGradientTo = change_lumi(theme_color["highlightColor"], 25),
        primaryGradientFrom = change_lumi(theme_color["selectionBackground"], -25),
        primaryGradientTo = theme_color["selectionBackground"],
        primaryHover = theme_color["accentColor"],
        highlightShadowColor = theme_color["foldedTextBackground"],
        errorGradientFrom = to_rgba(theme_color["errorColor"], 0.2),
        errorGradientTo = to_rgba(theme_color["errorColor"], 0.3),
        **theme_color
    )
    return css

def save_settings(theme_select, file_bg, bg_align, bg_opacity):
    """
    Saves the settings to a local file (settings.json).

    @param theme_select {str} Theme selected. Should be within the keys of dokithemejupyter.themes.themes.
    @param file_bg {tempfile._TemporaryFileWrapper} The temporary file uploaded to Web UI backend.
    @param bg_align {str} Alignment of background, e.g. chaos neutral or lawful good.
    There can be different alignments (see MDN background-position section) but it shouldn't be useful in this
    case as you can simply photoshop the image instead.
    @param bg_opacity {float} Opacity of the background. A value of 0 turns off the background.
    @returns {str} Result string to display in the UI.
    """
    try:
        settings = {
            "theme" : "",
            "bg" : "",
            "bg_align" : "center" if bg_align is None else bg_align,
            "bg_opacity" : float(bg_opacity)
        }
        
        if theme_select in themes:
            settings["theme"] = theme_select
        else:
            settings["theme"] = ""

        if file_bg is None:
            if theme_select in themes:
                settings["bg"] = "https://doki.assets.unthrottled.io/backgrounds/wallpapers/transparent/{}".format(
                    themes[theme_select]["colors"]["stickerName"]
                )
                # Set opacity back to default value if bg is not present
                settings["bg_opacity"] = 0.08
            else:
                settings["bg"] = ""
                settings["bg_opacity"] = 0.08
        elif bg_opacity < 0.001:
            settings["bg"] = ""
            settings["bg_opacity"] = 0.08
        elif bg_opacity > 0.999:
            ext = os.path.splitext(file_bg.name)[1]
            shutil.copy(file_bg.name, os.path.join(self_dir, "bg{}".format(ext)))
            settings["bg"] = "/file=extensions/{}/bg{}".format(
                os.path.basename(self_dir),
                ext
            )
        else:
            image_data = cv2.imread(file_bg.name, cv2.IMREAD_COLOR)
            image_rgba = cv2.cvtColor(image_data, cv2.COLOR_RGB2RGBA)
            image_rgba[..., 3] = (image_rgba[..., 3] * settings["bg_opacity"]).astype(np.uint8)
            cv2.imwrite(os.path.join(self_dir, "bg.webp"), image_rgba, [cv2.IMWRITE_WEBP_QUALITY, 90])
            settings["bg"] = "/file=extensions/{}/bg.webp".format(
                os.path.basename(self_dir)
            )
            
        with open(os.path.join(self_dir, "theme_settings.json"), "w", encoding = "utf-8") as fp:
            json.dump(settings, fp)

        return "Settings updated: {}\nRestart Web UI or Restart Gradio in Settings to see effects!".format(json.dumps(settings))

    except Exception as ex:
        return "Error: {}".format(ex)

def add_tab():
    """
    Adds a tab in the Automatic Stable Diffusion UI.

    @returns {list(tuple)} Callback format in the Automatic Stable Diffusion UI Extension format.
    """
    # load settings
    with open(os.path.join(self_dir, "templates", "tempura.css"), encoding = "utf-8") as fp:
        css_template = fp.read()

    with open(os.path.join(self_dir, "templates", "background.css"), encoding = "utf-8") as fp:
        css_template_bg = fp.read()

    try:
        with open(os.path.join(self_dir, "theme_settings.json"), encoding = "utf-8") as fp:
            settings = json.load(fp)
    except:
        settings = {
            "theme" : "",
            "bg" : "",
            "bg_align" : "right",
            "bg_opacity" : 0.08
        }

    # bg
    if len(settings["bg"]) <= 0 or settings["bg"].lower() == "none":
        css_bg = ""
    else:
        if settings["bg_align"] == "random":
            # the chaos evil option. Best used with a tiling image
            alignment = "{}% {}%".format(
                np.random.random() * 100,
                np.random.random() * 100
            )
        else:
            alignment = settings["bg_align"]
        css_bg = css_template_bg.format(
            img = settings["bg"],
            align = alignment,
            opacity = settings["bg_opacity"]
        )

    # theme
    theme = settings["theme"]
    if theme not in themes:
        css = ""
    else:
        css = generate_gradio_css(css_template, themes[theme]['colors'])

    with gr.Blocks(analytics_enabled=False, css=css) as ui:
        gr.HTML(f"""
            <style>{css} {css_bg}</style>
        """)
        theme_select = gr.Dropdown(label="Theme", value=settings["theme"], choices = list(themes.keys()))
        file_bg = gr.File(label="Background Image")
        bg_align = gr.Dropdown(label="Background Align", value=settings["bg_align"], choices=[
            "left",
            "center",
            "right",
            "center -5%",
            "center -10%",
            "center -15%",
            "random",
        ])
        bg_opacity = gr.Slider(0, 1, value=settings["bg_opacity"], label="Background Opacity")
        update = gr.Button(value="Save Settings", variant='primary')

        result = gr.Text(value="", show_label=False)

        update.click(
            fn=save_settings,
            inputs=[
                theme_select,
                file_bg,
                bg_align,
                bg_opacity
            ],
            outputs=result
        )

    return [(ui, "Themes", "themes")]

script_callbacks.on_ui_tabs(add_tab)
