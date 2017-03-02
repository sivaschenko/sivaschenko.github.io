---
layout:     post
title:      Magento 2 Varnish cache invalidation
date:       2017-01-09 08:30:06
summary:    Magento 2 CE has built-in Varnish cache invalidation functionality supporting several cache servers and invalidation by tags. This functionality can be easily overlooked because it is not explicit enough, there is even no UI related to it.
categories: magento2,varnish
---

## Introduction

Magento 2 CE has built-in Varnish cache invalidation functionality supporting several cache servers and invalidation by tags. This functionality can be easily overlooked because it is not explicit enough, there is even no UI related to it.

Varnish cache invalidation works the same way as built-in cache invalidation. However, cache servers credential should be configured using deployment configuration (instead of admin panel system configuration) and the functionality is implemented in a separate module.

## Module Functionality Overview

Cache invalidation functionality is introduced by **Magento_CacheInvalidate** module. This is a very tiny module that consists just of a couple of models and couple of observers, however, it is using much of **Magento_PageCache** module code.

The invalidation is performed by sending ```PURGE``` request to Varnish server **host:port**. The purge request includes ```X-Magento-Tags-Pattern``` header that enables cache invalidation by tags.

## Varnish side functionality

The PURGE request should be handled on Varnish side by the first part of ```vcl_recv``` function in vcl file:

```VCL
if (req.method == "PURGE") {
        if (client.ip !~ purge) {
            return (synth(405, "Method not allowed"));
        }
        if (!req.http.X-Magento-Tags-Pattern) {
            return (synth(400, "X-Magento-Tags-Pattern header required"));
        }
        ban("obj.http.X-Magento-Tags ~ " + req.http.X-Magento-Tags-Pattern);
        return (synth(200, "Purged"));
    }
```

That code is present is sample configuration file that can be exported from *Admin Panel -> Stores -> Configuration -> Advanced -> System -> Full Page Cache* fieldset.
The template for it is actually from **Magento_PageCache** module, [see in github](//github.com/magento/magento2/blob/develop/app/code/Magento/PageCache/etc/varnish4.vcl).

I would like to note that cache is not actually purged, it is banned while still remaining in memory, that fact has a positive impact on the time required to flush the cache, however, can cause some inconvenience in long run.

## Magento side functionality

On Magento side, the logic is represented by two observers **FlushAllCacheObserver** and **InvalidateVarnishObserver**.

The first one is sending ```X-Magento-Tags-Pattern: .*``` header that will ban all page cache. This observer is subscribed to the following events:

- ```adminhtml_cache_flush_system```
- ```clean_media_cache_after```
- ```clean_catalog_images_cache_after```
- ```adminhtml_cache_refresh_type```
- ```adminhtml_cache_flush_all```
- ```assign_theme_to_stores_after```

The **InvalidateVarnishObserver** is designed to flush cache by tags when entities are saved, so it's listening to the next events:

- ```clean_cache_by_tags``` (event is not dispatched in core modules, so looks like created for communtity use)
- ```assigned_theme_changed```
- ```catalogrule_after_apply```
- ```controller_action_postdispatch_adminhtml_system_currency_saveRates```
- ```controller_action_postdispatch_adminhtml_system_config_save```
- ```controller_action_postdispatch_adminhtml_catalog_product_action_attribute_save```
- ```controller_action_postdispatch_adminhtml_catalog_product_massStatus```
- ```controller_action_postdispatch_adminhtml_system_currencysymbol_save```
- ```clean_cache_after_reindex```

That observer is retrieving an object from the event instance. Only if the object is an instance of ```\Magento\Framework\DataObject\IdentityInterface``` observer is able to retrieve tags for invalidation using ```getIdentities``` method of the object.

Currently, not all entities in Magneto 2 are implementing that interface, so automatic full page cache invalidation (both for reverse-proxies and built-in cache) will not work for all entities.

## Enabling Varnish cache invalidation

To enable Varnish cache invalidation, three conditions should be satisfied:

- Full Page Cache should be enabled on *Admin Panel -> System -> Cache Management* page
- Caching Application should be set to "Varnish Cache" in *Admin Panel -> Stores -> Configuration -> Advanced -> System -> Full Page Cache* fieldset
- Varnish servers hosts:ports should be specified in deployment configuration.

To add Varnish servers to deployment configuration it is convenient to use Magento command:

```Shell
bin/magento setup:config:set --http-cache-hosts=127.0.0.1:80,192.0.1.100:81
```

This will update ```app/etc/env.php``` file with the following snippet:

```php?start_inline=1
'http_cache_hosts' =>
    array(
        0 =>
            array(
                'host' => '127.0.0.1',
                'port' => '80',
            ),
        1 =>
            array(
                'host' => '192.0.1.100',
                'port' => '81',
            ),
    ),
```
