---
layout:     post
title:      5 block types from caching point of view in Magento 2
date:       2017-03-10 21:30:06
summary:    Here is my classification of blocks in the context of caching, or five approaches to caching, and my thoughts on when and how to use them. This covers both full page and block cache.
categories: magento2,performance
twitterimage: /images/thumbnails/magento2-full-page-and-block-cache-types.jpg
---

Here is my classification of blocks in the context of caching, or five approaches to caching, and my thoughts on when and how to use them. This covers both full page and block cache.

## Cacheable

Block is cacheable (for block cache) if ```cache_lifetime``` of the block is set to a number greater than 0.

Use when the block:

 - is frequently used, i.e. the same block with the same content is displayed on several pages.
 - is a cacheable part of non-cacheable page.

How to use:

 - Setting ```cache_lifetime``` from layout XML:

```xml
<block class="MyBlock">
    <arguments>
        <argument name="cache_lifetime" xsi:type="number">3600</argument>
    </arguments>
</block>
```

 - Setting ```cache_lifetime``` from DI configuration:

```xml
<type name="MyBlock">
    <arguments>
        <argument name="data" xsi:type="array">
            <item name="cache_lifetime" xsi:type="number">3600</item>
        </argument>
    </arguments>
</type>
```

 - Setting ```cache_lifetime``` magically and in imperative way:

```php?start_inline=1
$block->setCacheLifetime(3600);
// or
$block->setData('cache_lifetime');
```

 - Overriding retriever method (common in core modules for some reason):

```php?start_inline=1
class MyBlock extends AbstractBlock
{
    protected function getCacheLifetime()
    {
        return 3600;
    }
}
```

## Non-cacheable block

Block is non-cacheable (for block cache) if ```cache_lifetime``` of the block is NOT set to a number greater than 0. **By default all blocks are non-cacheable.**

Use when the block:

 - has dynamic content and is unlikely to be rendered with equal content several times.
 - is used only as a child of a cacheable block in layout hierarchy.

How to use:

 - do not apply anything from previous "How to use" section.

## Page cache killer

Page cache killer is a block that has ```cacheable``` attribute set to ```false``` in the layout declaration. If at least one such block is present on a page, the entire page is not cacheable for Full Page Cache.

Use when the block:

 - is rendering private content but is not private (see next type)
 - is rendering content that should be shown only once
 - is rendering content that is frequently updated
 - business logic implementation contains calls to functions such as rand() or mt_rand()

How to use:

Set cacheable attribute of block node in layout XML to false:

```xml
<block class="MyBlock" cacheable="false"/>
```

## Private

Block is private if ```_isScopePrivate``` property of block class is set to ```true```. Private blocks are rendered in two stages. Main response contains only a placeholder for the private block. Separate AJAX request is retrieving actual content and puts it instead of the placeholder.

Use when the block:

 - is rendering private (session related) information on a cacheable page
 
How to use:

Set protected property of AbstractBlock ```_isScopePrivate``` to ```true```
```php?start_inline=1
$this->_isScopePrivate = true;
```

## ESI

Block is ESI if it's declaration in the layout XML has ```ttl``` attribute. ESI blocks are actual only if full page cache application is set to Varnish. Such blocks are fetched by separate Varnish request, cached and invalidated independently from the page.

Use when the block:

 - is supposed to be invalidated much-much more frequently than pages where this block is rendered
 - is supposed to be invalidated much-much less frequently than pages where this block is rendered
 
How to use:

Add TTL attribute to block declaration in layout

```xml
<block class="MyBlock" ttl="3600"/>
```

Let me know if we can identify additional types or improve existing types description!