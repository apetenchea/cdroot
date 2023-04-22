# cdroot

This is the source of https://apetenchea.github.io.  
If you want to set up a similar blog, here's a nice [article](https://angelkyriako.github.io/2017/01/24/hexo-tutorial/).

## Additional dependencies
In case you ever need to reinitialize the blog, install these packages afterwards.
```
npm install hexo-deployer-git --save
npm install hexo-renderer-marked --save
npm install hexo-tag-github-code --save
npm install mathjax@3 --save
```
In order to host [MathJax](https://github.com/mathjax/MathJax) yourself, move the `es5` folder into `source/javascript/mathjax`:
```bash
mv node_modules/mathjax/es5 source/javascript/mathjax
```
At the bottom of the pages that use MathJax, add the following line:
```html
<script id="MathJax-script" async src="/javascript/mathjax/tex-chtml.js"></script>
```

## Hexo commands
`hexo -v` - version information  
`hexo init cdroot` - initialize site (only during repo creation)  
`hexo server` - start local server  
`hexo new post "title"` - create a new post  
`hexo s -o` - start server and open the blog page in browser

## Deploy
```
hexo clean
hexo generate
hexo deploy
```