---
layout:     post
title:      Magento 2. Adding column to Sales Order grid
date:       2016-03-05 11:21:29
summary:    First of all, ensure you have your column in database table, and it is mapped to any field of sales_order table. Don't worry about implications of core table modification. sales_order_grid is index table and is used for order grid rendering speed up. It is designed to store all information required for sales order grid rendering, so custom columns are required to be added to this table.
categories: magento2
---

Sales order grid in Magento 2 can be accessed in admin panel under "Sales" -> "Orders" menu.
By default only several main columns are visible in grid, but there are additional columns, that can be enabled from "Columns" dropdown on the top-right side.

![Magento 2 Sales Order Grid Columns]({{ site.url }}/images/magento2-sales-order-grid-columns.png)

However, if you are creating a module that provides additional useful information about orders, it is a good idea to add corresponding columns to sales order grid.

Basically, to add a column to sales order grid you have to perform 3 simple steps:

 - Add column to **sales_order_grid** database table
 - Add DI configuration to populate the column in **sales_order_grid** table with your value
 - Add UI component configuration to display the column in grid
 
Let's go through this implementation step by step.

## Preconditions

First of all, ensure you have your column in database table, and it is mapped to any field of **sales_order** table. For my example, let's assume that there is **affiliate** table consisting of two columns: **order_id** and **affiliate_information**. This table is used to store some [affiliate information](http://en.wikipedia.org/wiki/Affiliate_marketing) related to particular order. It would be nice to display this information in "Affiliate Information" column in sales order grid. Let's do this!

## Adding column to sales_order_grid database table

Columns are added to database tables using **InstallSchema** script. To be consistent, this script should be updated in the same module, where affiliate table was added.

The following code fragment will do the trick:

```php?start_inline=1
$setup->getConnection()->addColumn(
    $setup->getTable('sales_order_grid'),
    'affiliate_information',
    [
        'type' => Table::TYPE_TEXT,
        'comment' => 'Affiliate Information'
    ]
);
```

Just add it to ```app/code/<your_namespace>/<your_module>/Setup/InstallSchema.php``` file and it will create a column named **affiliate_information**, of type text, with comment "Affiliate Information" to **sales_order_grid** during installation.

Don't worry about implications of core table modification. **sales_order_grid** is index table and is used for order grid rendering speed up. It is designed to store all information required for sales order grid rendering, so custom columns are required to be added to this table.

To reflect changes in database magento reinstallation is required. Optionally, deleting module entry from setup_module table and running bin/magento setup:upgrade command will be also ok.

After this step, **affiliate_information** column is present in **sales_order_grid** table, but is remaining empty as it is not mapped to any data source.

## DI configuration to populate the column is sales_order_grid table.

On this stage, it would be good to understand how **sales_order_grid** table is populated.

When order is placed (according to default configuration), data related to this order is selected from **sales_order** table joining several additional tables and inserted to **sales_order_grid**. This operation is initiated by ```\Magento\Sales\Model\ResourceModel\Grid::refresh``` function and the default select is declared in "\<Magento Sales module>/etc/di.xml" file.

So to include our table in mentioned insert from select, we have to extend di configuration creating ```app/code/<Namespace>/<Module>/etc/adminhtml/di.xml``` file.

The following xml snippet should be added to di configuration inside config node.

```xml
<config ...>
    ...
    <virtualType name="Magento\Sales\Model\ResourceModel\Order\Grid">
        <arguments>
            <argument name="joins" xsi:type="array">
                <item name="affiliate" xsi:type="array">
                    <item name="table" xsi:type="string">affiliate</item>
                    <item name="origin_column" xsi:type="string">entity_id</item>
                    <item name="target_column" xsi:type="string">order_id</item>
                </item>
            </argument>
            <argument name="columns" xsi:type="array">
                <item name="affiliate_information" xsi:type="string">affiliate.affiliate_information</item>
            </argument>
        </arguments>
    </virtualType>
    ...
</config>
```

This configuration is specifying that affiliate table will be joined to select from **sales_order** on ```sales_order.entity_id = affiliate.order_id``` and will populate **sales_order_grid.affiliate_information** column with corresponding value from **affiliate.affiliate_information**.

After this step, our affiliate_information column in **sales_order_grid** table is populated with value from affiliate table each time order is placed. Still, column will exist only in database, and will not be visible in admin panel.

## Configure UI grid component to display the column

Finally, to reflect the column on admin panel grid, we have to extend **sales_order_grid** ui component by adding a ui configuration file in our module.

It is possible to extend ui configuration fo sales order grid introducing ```app/code/<Namespace>/<Module>/view/adminhtml/ui_component/sales_order_grid.xml``` file.
Basically it should have the same name and path in relation to module directory as main sales order grid ui component file: ```app/code/Magento/Sales/view/adminhtml/ui_component/sales_order_grid.xml```

Put the following xml snippet to the ui configuration file:

```xml
<listing ...>
    <columns name="sales_order_columns">
        <column name="affiliate_information">
            <argument name="data" xsi:type="array">
                <item name="config" xsi:type="array">
                    <item name="filter" xsi:type="string">text</item>
                    <item name="label" xsi:type="string" translate="true">Affiliate Information</item>
                </item>
            </argument>
        </column>
    </columns>
</listing>
```


This will extend sales_order_columns and add a column based on **affiliate_information** filed, of type text, with translatable label "Affiliate Information".

## Ensuring sales_order_grid is populated after value is inserted to source table.

There are two approaches to ensure that correct value is present in source table when **sales_order_grid** is populated:

 - Save value to source table before **sales_order_grid** refresh is triggered.
 - Trigger **sales_order_grid** refresh after saving value.
 
First approach is necessary if value should be saved to source table right on place order action. One of solutions will be to create observer on event that is dispatched when order is saved, but grid is still not refreshed. Such event is ```sales_order_save_after```.

Second approach is applicable when source table is updated some time after order is placed, or asynchronously. Here you have to call ```\Magento\Sales\Model\ResourceModel\Grid::refresh``` method after value is saved to source table.

## Populating created sales_order_grid column for existing order

For upgrading existing data either install (for first release of your module) or upgrade script should be created.

Here is an example of upgrade script populating ```sales_order_grid.affiliate_information``` column from ```affiliate.affiliate_information``` for 1.0.1 version of module.

```php?start_inline=1
namespace YourNamespace\YourModule\Setup;

use Magento\Framework\Setup\ModuleContextInterface;
use Magento\Framework\Setup\ModuleDataSetupInterface;
use Magento\Framework\Setup\UpgradeDataInterface;

class UpgradeData implements UpgradeDataInterface
{
    /**
     * {@inheritdoc}
     */
    public function upgrade(ModuleDataSetupInterface $setup, ModuleContextInterface $context)
    {
        $setup->startSetup();

        if (version_compare($context->getVersion(), '1.0.1', '<')) {
            $connection = $setup->getConnection();
            $grid = $setup->getTable('sales_order_grid');
            $affiliate = $setup->getTable('affiliate');

            $connection->query(
                $connection->updateFromSelect(
                    $connection->select()
                        ->join(
                            $affiliate,
                            sprintf('%s.entity_id = %s.order_id', $grid, $affiliate),
                            'affiliate_information'
                        ),
                    $grid
                )
            );
        }

        $setup->endSetup();
    }
}
```

For this upgrade script to be executed, you have to increase module version in module.xml (from 1.0.0 to 1.0.1) and run ```bin/magento setup:upgtade``` command

## Final Tips

Be sure to refresh config cache after editing xml files.

Provided setting are basic, and there are much more parameters available for install script, di and ui configuration to customize content and appearance of added column, take time to observe existing install scripts, di and ui configuration files and try adding more parameters to your implementation.

Hope this tutorial was useful for you. Please feel free to provide any feedback in comments or contact me directly.