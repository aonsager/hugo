---
category: 1.1-software-development
title: Missingno. in Pokemon Fusion
date: 2014-08-10 18:49:00
tags:
  - pokemon
  - missingno
  - fusion
  - artwork
  - imagemagick
  - sprites
  - glitches
colors:
  - "#b8b5b8"
  - "#cac7c3"
  - "#96817e"
  - "#b9babc"
  - "#e35560"
metaRSS: true
---

I've made a small update to the [Pokemon Fusion](http://pokemon.alexonsager.net) site, and added Missingno. as a hidden pokemon.

I was inspired by the incredible Mewtwo x Missingno. fusion artwork that was posted by StarvingStudents on his [deviantART page](http://starvingstudents.deviantart.com/art/Mewssingno-472862222)

Missingno. appears whenever there is an invalid ID in the URL, so acts as a fun 404 page. You can try it out [here](http://pokemon.alexonsager.net/25/0)

![Pikassingno.](/images/pikassingno.png)

The glich images were generated with ImageMagick (the Rmagick ruby gem in particular), using the spread function to displace pixels by a certain amount. In this case, I also shrunk the image first to exaggerate the pixelation, and it brought it back to normal size afterwards.

```ruby
filename = "pokemonimage.png"
img = Magick::ImageList.new(filename)
img.resize!(40, 40, Magick::PointFilter)
img = img.spread(2)
img.resize!(160, 160, Magick::PointFilter)
```

The `Magick::PointFilter` option is what allows us to preserve the blocky pixels when we resize, because otherwise ImageMagick will try to smooth out the edges for us.

As a finishing touch, I also sprinkled in some pixels of the purple and orange that are used in Missingno.'s sprite.
