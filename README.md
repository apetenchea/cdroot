# cdroot

This is the source of https://apetenchea.github.io.  
If you want to set up a similar blog, here's a nice [article](https://angelkyriako.github.io/2017/01/24/hexo-tutorial/).

## Additional dependencies
In case you ever need to reinitialize the blog, install these packages afterwards.
```
npm install hexo-renderer-kramed --save
npm install hexo renderer-mathjax --save
npm install hexo-deployer-git --save
npm install hexo-renderer-marked --save
npm install hexo-tag-github-code --save
```

## Hexo commands
`hexo -v` - version information  
`hexo init cdroot` - initialize site (only during repo creation)  
`hexo server` - start local server  
`hexo new new-post` - create a new post  
`hexo new draft new-draft` - create a new draft  
`hexo new publish new-draft` - publish draft  
`hexo s -o` - start server and open the blog page in browser

## Deploy
```
hexo clean
hexo deploy
```