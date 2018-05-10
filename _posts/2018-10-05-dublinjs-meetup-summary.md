---
layout:     post
title:      DublinJS Meetup Summary (May 2018)
date:       2018-05-10 08:30:06
summary:    First time I was attending a meetup in the lightning talks format. 12 speakers presented a short 5 minute talk each. The approach impressed me by it's energizing dynamics and the volume of filtered, only valuable information on every topic.
categories: javascript,meetup
twitterimage: /images/thumbnails/dublinjs-speakers.jpg
---

First time I was attending a meetup in the lightning talks format. 12 speakers presented a short 5 minute talk each. The approach impressed me by it's energizing dynamics and the volume of filtered, only valuable information on every topic.

I wasn't able to capture everything to my records, however, still quite a lot, here are my notes:

## What does 'this' mean in JS - Jose Padilla

Jose demonstrated several cases of how object context can impact the result of function execution.

The funny thing was that "Father Jack" tv series was used for ideas behind the code examples. It is possible to set context object for a function using ```.bind()``` method.

## Newrelic - Lucy Lu

Lucy demonstrated general [Newrelic](https://newrelic.com) features for tracking performance and stability of your websites.

## Experimental Web Browser API - Shane Healy

An amusing presentation of interesting Browser APIs available for javascript.

Did you know that there is a browser API providing information on the battery charge and if the laptop is currently charging?

Also, there are a lot of experimental browser APIs that can be enabled in "Experimental Web Platform Features" section of Chrome settings.

## Mobile optimized payments with Stripe Elements - Thorsten Schaeff

Demonstrated awesome cross-platform and configurable e-commerce checkout frontend via Stripe. [See Demo here](http://stripe-payments-demo.appspot.com)!

[@thorwebdev](https://twitter.com/thorwebdev)

## Using puppeteer for UI testing - Noel Ryan

Showed an approach for UI testing using [Puppeteer](https://developers.google.com/web/tools/puppeteer/) that includes taking and storing screenshots and comparing them to sreenshots taken on the previous run (with Pixelmath).

## Rendering Markdown In The Javascript Console - Adam Kelly

There is so much you can do in the console apart from just logging borring debug information! The console supports rendering of tables, arrays/objects and even styles.

```js
console.log('%c Hello world! ', 'background: #222; color: #bada55');
```

Check out [Adam's tool for rendering markdown in js console](https://github.com/adamisntdead/console.md)!

```
npm install console-markdown
```

[@adamisntdead](https://twitter.com/adamisntdead)

## Data visualisation using maps - Ramona

Ramona showed a web-GL data visualisation library developed by Uber (with [Mapbox](https://www.mapbox.com/about/maps/)): [deck.gl](https://uber.github.io/deck.gl/#/examples/core-layers/geojson-layer)

Be careful as the library utilizes GPU resources and the result (performance) depends on a machine it is running on!

[@CodesOfRa](https://twitter.com/CodesOfRa)

## Creating PWAs with Ember.js - Kevin Fagan

Kevin showed how handy it is to use [Ember.js](https://www.emberjs.com/) library for creating progressive web applications.

A lot of code and commands were featured! Here is a snippet I managed to remember:

```
ember install ember-service-worker-index
ember install ember-service-worker-asset-cache
ember install ember-service-worker-cache-fallback
ember install ember-cli-fastboot
npm install —save fastboot-app-server
ember install …-manifest
```

## Google Drive API - Sheldon Led

Sheldon showed how Google Drive API can be used by web applications to save and load files.

[@sheldonled](https://twitter.com/sheldonled)

Also, I discovered quite a lot of interesting presentation on [Sheldon Leds website](http://github.sheldonled.com/talks/)

## Simple website’s colors and components generator - Maksym Shykula

Max showed a nice tool he created for website style generation: [QuackUI](http://quackui.org/)

The interesting thing is that the tool not only picks a color palette and element styles, but also has database of images that are picked based on the colors.

The website can be used to download ready and clean CSS file.

## Machine learning in JavaScript - Omar Sucapuca

Omar demonstrated javascript Machine Learning models by [TensorFlow.js](https://js.tensorflow.org)

The ML demo using a web cam can be [accessed here](https://storage.googleapis.com/tfjs-examples/webcam-transfer-learning/dist/index.html)!

[@omar_suca](https://twitter.com/omar_suca)

## Http request lifecycle - Ingrid Epure

Ingrid reminded us how hard and complex is actually a lifecycle of a simple http requests, starting from DNS lookup and down to database query caching.

[@ingridepure](https://twitter.com/ingridepure)

## Thanks

That was one of the best meetups I was attending so far. Big thanks to organizers, speakers and sponsors!

Please let me know if I should add or update anything! Also, it would be great if you could share missing speaker/presentation contacts/references!