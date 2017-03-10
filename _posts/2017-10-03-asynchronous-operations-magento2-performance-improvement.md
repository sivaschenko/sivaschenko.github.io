---
layout:     post
title:      Asynchronous operations for Magento 2 performance improvement
date:       2017-03-10 08:30:06
summary:    While infrastructure tuning can result in regular additional costs, it still can only soften the impact of application architecture and algorithms. It is code that stands behind application performance first. That's why it is important to always keep in mind performance implications while customizations and especially extensions development.
categories: magento2,performance
twitterimage: /images/thumbnails/async-all-the-things.jpg
---

## Introduction

There are various practices for performance optimization of Magento 2 website on code and infrastructure level. While infrastructure tuning can result in regular additional costs, it still can only soften the impact of application architecture and algorithms. It is code that stands behind application performance first. That's why it is important to always keep in mind performance implications while customizations and especially extensions development. However, code optimization may sometimes be a compromise between functionality and speed. And sometimes it's just not possible to avoid or optimize execution of a resource consuming operation. However, such operations can still be executed asynchronously avoiding any impact on the page response time.

While ideally the asynchronous operations I will be writing about should be performed using special external worker applications, there is always an opportunity to implement these, without any additional dependencies, using available Magento Cron jobs.

## Asynchronous operations in Magento 2 out of the box

Generally speaking a lot of operation in Magento 2 are performed by Cron asynchronously. But in this article, I will focus on the operations that are usually part of request processing, and have been or can be extracted as asynchronous operation for the purpose of performance improvement.

Lets take a look at the most critical operation for E-commerce: place of an order. Place of an order is probably the most resource consuming request a customer can trigger.

Application has to authorize payment, create order document, send an order confirmation email, update admin panel grids and much more without even considering a variety of available integrations.

Magento 2 introduces two operations that can be configured as asynchronous, providing a good example for the community.

1. Order confirmation email is not an operation that should instantly happen and can be processed several minutes later, removing extra load from place order request processing.

This operation can be switched to asynchronous from Admin Panel "Stores" -> "Configuration" -> "Sales" -> "Sales Emails" -> "General Settings".

![Magento 2 Asychronous Order Confirmation Emails Configuration Switch]({{ site.url }}/images/order-confirmation-emails-asynchronous-configuration-switch.png)

2. A similar switch is provided for reindexing ```sales_order_grid``` table, that is also a resource consuming one.

It can be accessed from "Stores" -> "Configuration" -> "Advanced" -> "Developer" -> "General Settings".

![Magento 2 Order Grid Asychronous Indexing Configuration Switch]({{ site.url }}/images/order-grid-asynchronous-indexing-configuration-switch.png)

While I strongly recommend you to ensure those two switches are "Enabled" on your production Magento instance, lets go further and see how to follow this Magento practice and extract asynchronous operations from your extension.

## Extracting asynchronous operation

As an example of operation, I would like to use additional action that also should be triggered during placing of an order.

Let's say we'd like to implement an integration that reflects/forwards placed order to an external ERP.

For the elementary asynchronous operation implementation only 3 components are essential:

 - DB status table holding order id and a flag if order was successfully delivered to 3rd party application
 - Processor class performing the operation and triggered by Cron
 - Cron configuration
 
### Creating database table

First, we need a DB table holding statuses. It's a simple two-column table that can be created using an example of install schema script underneath:

```php
<?php

namespace YourNamespace\YourModule\Setup;

use Magento\Framework\Setup\ModuleContextInterface;
use Magento\Framework\Setup\SchemaSetupInterface;

class InstallSchema implements \Magento\Framework\Setup\InstallSchemaInterface
{
    public function install(SchemaSetupInterface $setup, ModuleContextInterface $context)
    {
        $setup->startSetup();

        $table = $setup->getConnection()->newTable(
            $setup->getTable('external_integration_order')
        )->addColumn(
            'order_id',
            \Magento\Framework\DB\Ddl\Table::TYPE_INTEGER,
            null,
            ['unsigned' => true, 'nullable' => false, 'primary' => true],
            'Order ID'
        )->addColumn(
            'status',
            \Magento\Framework\DB\Ddl\Table::TYPE_SMALLINT,
            null,
            ['nullable' => false, 'default' => 0],
            'Status. 1 - if operation was successfully performed.'
        );
        $setup->getConnection()->createTable($table);
        
        $setup->endSetup();
    }
}
```

### Cron processor class

Now, here is a quick example of processor class. The main idea is to get all orders without any records in ```external_integration_order``` table. And perform required operation for them.

```php
<?php

namespace YourNamespace\YourModule\Cron;

class ExternalIntegrationNotify
{
    private $notifier;

    private $collectionFactory;

    public function __construct(
        \YourNamespace\YourModule\Model\Notifier $notifier,
        \Magento\Sales\Model\ResourceModel\Order\CollectionFactory $collectionFactory
    ) {
        $this->notifier = $notifier;
        $this->collectionFactory = $collectionFactory;
    }

    public function execute()
    {
        $collection = $this->collectionFactory->create();
        $connection = $collection->getSelect()->getConnection();

        $collection->getSelect()
            ->joinLeft(
                ['eio' => $connection->getTableName('external_integration_order')],
                'main_table.entity_id = eio.order_id',
                ['status' => 'eio.status']
            )
            ->where('eio.status is null')
            ->orWhere('eio.status != 1');

        $orderStatuses = [];
        foreach ($collection as $order) {
            $orderStatuses[$order->getId()] = $this->notifier->performOperationForOrder($order);
        }
        //Only the update of status in external_integration_order table is remaining
    }
}
```

### Cron configuration

Finally, a Cron configuration file that will trigger ```ExternalIntegrationNotify::execute``` should be created inside ```etc``` module directory.

In this case, the job is configured to execute each 5 minutes.

```xml
<?xml version="1.0"?>
<config xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xsi:noNamespaceSchemaLocation="urn:magento:module:Magento_Cron:etc/crontab.xsd">
    <group id="default">
        <job name="external_integration_notification" instance="YourNamespace\YourModule\Cron\ExternalIntegrationNotify" method="execute">
            <schedule>*/5 * * * *</schedule>
        </job>
    </group>
</config>
```

### Further code improvements

The code provided here is shortened and not ideal. For sure it would be better to handle DB queries inside corresponding resource model, probably add a foreign key to the table (however what can happen with placed order in Magento?), and so on.

Additionally, you can consider involving a configuration and returning from ```ExternalIntegrationNotify::execute``` without performing anything if configuration is set to synchronous while having additional observer/plugin that will be a synchronous alternative. But, be sure to call ```ExternalIntegrationNotify::execute``` on the moment when the configuration is switched from async to sync execution, not to forget pending orders.

Cron configuration can also be made more flexible by replacing ```schedule``` with ```config_path``` node, so that frequency of executions can also be set from admin panel.

As a bonus, consider dedicated status for problematic orders (i.e. if some order fails to be processed by integration), and displaying this status in sales order grid (that can be done using instructions from [another my article]())

If you have more ideas, any feedback or improvement suggestions for this material - feel free to share it in comments.

## Conclusion

Examples in this article are all around place order action, however, the practice described can be applied in many more places.

If you know a good candidate to move to asynchronous execution in Magneto 2, it would be good to bring it up to the community and Magento Team. Lets discuss how we can make Magento 2 faster together.

