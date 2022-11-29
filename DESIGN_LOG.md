tailwind native color customization doesnt work, dunno why.
anyways it was a bad idea, shouldn't have to go through build process
just to change a css theme (imaging rebuilding every time either gradio
or unthrottled or automatic updates the thing)

1. implement every doki CSS separately in a bunch of CSS files
 > transform a css-built unthrottled repo to tailwind hacking form
 > try abusing css priority, if it doesnt work add !important
 > looks like duplicating class selector is the best option!
2. add a settings panel such that when a user sets theme and bgimage,
   it goes through a python process to set transparency (dont do it in css)
   of the bgimage and adds in the final styles.css file
3. use the automaticui api to add the css file, and js file to add
   dark mode if necessary (the only switch should be light/dark so we can python)

for using it on other gradio, make it some trigger (callable from python)
to somehow add the css to gradio output, then leave the dark mode to its
original settings ("it follows system pref")
^ seems a lot of themes have only light/only dark, this is unimplementable

workflow:

1. for each color in gradio template:
   1) find out where it is used in Kitchen Sink Demo
   2) find an equivalent element in Github
   3) use the color from unthrottled github theme

primaryGradientFrom, primaryGradientTo, primaryHover = selection-background

questions:

1. can we align tailwind color table to unthrottled colors with diff. luminance?
 > use some sort of ML model? or perhaps its simple as stuff like LAB/deltaE
 > might be only useful if we want to make "Doki-Theme-Tailwind"
 ^ pretty sure it needs customization if we gonna add it to other gradio projects
 ^ which in the end would need to either let their dev choose the color type
 ^ or we recolor tailwind entirely (nope)
2. do we always use same color assignment as global/tokens.css?
 > is there any part we would want to separate colors that was originally same?
 ^ turned out we don't just need that, need a lot more even for vanilla gradio
 ^ most of the colors were for code highlight
 ^ technically gradio has one but directly tailwind, gonna leave it as-is
3. background opacity in the CSS?
 > can do with pseudoelements. but what about performance?
 > easier to deal with JPGs, and no need for a compression if we do python
 ^ this causes backgrounds on other elements not to display correctly
 ^ unless we going to add pseudoelement on every single div that has background
 ^ so went with cv2 opacity adjustment, compression solved by cv2 webp options
4. should we just pip install doki-theme-jupyter?
 > this installs jupyter on the web UI which is totally unnecessary
 > they have a master-themes which has the source data of dokithemes
 ^ too complicated and waste of time to compile
 ^ jupyter pretty irrelevant considering we have several gigs of models already

colors:

1. from-X-Y/Z to-X'-Y'/Z' makes gradient with opacity Z to Z'