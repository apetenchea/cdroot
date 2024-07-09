---
title: python asyncio
date: 2024-07-09 19:25:46
tags:
  - "Programming"
---

![Python Asyncio Heading Image](https://raw.githubusercontent.com/apetenchea/cdroot/master/source/_posts/python-asyncio/media/heading.jpg)

It's been a while since I delved into Python's asyncio module. Back in 2018, I became familiar with it, while working
on a massive machine learning pipeline for Bitdefender. It was the asyncio feature that allowed us to scale the entire thing without
needing to grow the number of CPU cores linearly, which as you can imagine, saved quite a bit of money.  
Fast-forward to 2024, I'm maintaining the [python-arango](https://github.com/arangodb/python-arango) driver, which is
synchronous by design. I've always wanted to write about asyncio, because I think it's such a game changer for Python developers.
Now that I started working on the long-awaited [python-arango-async](https://github.com/arangodb/python-arango-async),
it's a great opportunity to synthesize my knowledge here. This article is intended as a quick reference on the topic,
giving enough context to navigate the asyncio waters with confidence.

## Example

