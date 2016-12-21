---
layout:     post
title:      Magento 2. Retrieving category layered navigation filterable attributes
date:       2016-12-20 8:20:29
summary:    Retrieving layered navigation attributes is a useful task that can be required during optimization and implementaion of various features ...
categories: magento2
---

# Introduction

Retrieving layered navigation attributes is a useful task that can be required during optimization and implementaion of various features.

As usual, there is more than one way for achieving the goal.

I will start from the most primitive and fast approach, and continue with more framework utilization recommended for future maintainability.

# SQL Query

Basically the raw sql query will clearly describe what I am going to achieve:

Variant 1 (subselects):

```sql
SELECT eav_attribute.attribute_id
FROM eav_attribute
WHERE eav_attribute.attribute_id IN (
  SELECT catalog_eav_attribute.attribute_id
  FROM catalog_eav_attribute
  WHERE catalog_eav_attribute.is_filterable = 1
)
AND eav_attribute.attribute_id IN (
  SELECT eav_entity_attribute.attribute_id
  FROM eav_entity_attribute
    JOIN catalog_product_entity ON eav_entity_attribute.attribute_set_id = catalog_product_entity.attribute_set_id
    JOIN catalog_category_product ON catalog_product_entity.entity_id = catalog_category_product.product_id
  WHERE catalog_category_product.category_id = 1234
);
```

Variant 2 (joins):

```sql
SELECT
  eav_attribute.attribute_id
FROM eav_attribute
  JOIN eav_entity_attribute ON eav_attribute.attribute_id = eav_entity_attribute.attribute_id
  JOIN catalog_eav_attribute ON eav_attribute.attribute_id = catalog_eav_attribute.attribute_id
                             AND catalog_eav_attribute.is_filterable = 1
  JOIN catalog_product_entity ON eav_entity_attribute.attribute_set_id = catalog_product_entity.attribute_set_id
  JOIN catalog_category_product ON catalog_product_entity.entity_id = catalog_category_product.product_id
                                AND catalog_category_product.category_id = 1234
GROUP BY eav_attribute.attribute_id;
```

As you can see the attributes we need are **filterable attributes from attribute sets of products included in specified category**.

These sql queries will also help to test program realization later.

# Using Resource

Lets first try to perform the straight query using just a ```ResourceConnection``` (this approach can be used for prototyping or quick debug).

```php?start_inline=1
$categoryId = 1234;

$resource = ObjectManager::getInstance()->get(\Magento\Framework\App\ResourceConnection::class);
$connection = $resource->getConnection();

$select = $connection->select()->from(['ea' => $connection->getTableName('eav_attribute')], 'ea.attribute_id')
    ->join(['eea' => $connection->getTableName('eav_entity_attribute')], 'ea.attribute_id = eea.attribute_id')
    ->join(['cea' => $connection->getTableName('catalog_eav_attribute')], 'ea.attribute_id = cea.attribute_id')
    ->join(['cpe' => $connection->getTableName('catalog_product_entity')], 'eea.attribute_set_id = cpe.attribute_set_id')
    ->join(['ccp' => $connection->getTableName('catalog_category_product')], 'cpe.entity_id = ccp.product_id')
    ->where('cea.is_filterable = ?', 1)
    ->where('ccp.category_id = ?', $categoryId)
    ->group('ea.attribute_id');

$attributeIds = $connection->fetchCol($select);
```

Then attribute ids can be used to load collection of attributes.

```php?start_inline=1
$collectionFactory = ObjectManager::getInstance()->get(\Magento\Catalog\Model\ResourceModel\Product\Attribute\CollectionFactory::class);
$collection = $collectionFactory->create();
$collection->setItemObjectClass('Magento\Catalog\Model\ResourceModel\Eav\Attribute')
        ->addStoreLabel($this->storeManager->getStore()->getId());
$collection->addFieldToFilter('attribute_id', ['in' => $attributeIds]);
```

After this code is executed, ```$attributeIds``` is an array of filtable attribute ids involved in category with specified id.

However this implementation is not ideal, because it skips potentially extended behavior of layered navigation and small details like disabled, out of stock products, etc.

# Using Layer

After a bit of investigation I was not able to find framework api to provide filterable attributes for specific category.

So, the task is a bit more complex than seems to be.

Basically all filterable attributes in Magento 2 can be retrived from **FilterableAttributeList**:

```php?start_inline=1
$filterableAttributes = ObjectManager::getInstance()->get(\Magento\Catalog\Model\Layer\Category\FilterableAttributeList::class);
$attributes = $filterableAttributes->getList();
```

Retrieving filters involved in layered navigation is a bit more tricky.

```php?start_inline=1
$filterableAttributes = ObjectManager::getInstance()->get(\Magento\Catalog\Model\Layer\Category\FilterableAttributeList::class);

$appState = ObjectManager::getInstance()->get(\Magento\Framework\App\State::class);
$layerResolver = ObjectManager::getInstance()->get(\Magento\Catalog\Model\Layer\Resolver::class);
$filterList = ObjectManager::getInstance()->create(
    \Magento\Catalog\Model\Layer\FilterList::class,
    [
        'filterableAttributes' => $filterableAttributes
    ]
);

 $category = 1234;
 
 $appState->setAreaCode('frontend');
 $layer = $layerResolver->get();
 $layer->setCurrentCategory($category);
 $filters = $filterList->getFilters($layer);
```

Please be aware, that I am using object manager static calls just for short and explicit example. In clean implementation it is highly recommended to use di instead.

You might also want to use di configuration for defining ```filterableAttributes``` argument.

However this is not the final result. To be sure that filters are actual, it is required to check number of items for each filters. (that check is accually performed during core layered navigation [rendering](//github.com/magento/magento2/blob/develop/app/code/Magento/LayeredNavigation/view/frontend/templates/layer/view.phtml#L38))

```php?start_inline=1
foreach ($filters as $filter) {
    if ($filter->getItemsCount()) {
        $filters[] = $filter;
    }
}
```

In above code block you can also perform additional checks and i.e. throw away Price and Category filter instances, if you need just Attribute type filters.

Then filter name and values can be retrieved:

```php?start_inline=1
$name = $filter->getName();
foreach ($filter->getItems() as $item) {
    $value = $item->getValue();
}
```

Solutions mentioned here are the best I could find. However, they do not look perfect. So, if you know a better solution or at least can advise where to look, please leave a comment. I will much appreciate it!
