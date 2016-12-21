---
layout:     post
title:      Apache running multiple PHP versions simultaneously
date:       2016-11-22 11:21:29
summary:    Lets setup an Apache webserver to run PHP 5.6 and 7.0 websites simultaneously ...
categories: php
---

# Overview

There are several ways to achieve the same goal and run multiple websites on different PHP versions simultaneously.

In my opinion, the most convenient way to install several PHP versions side-by-side for development purpose is using **PHPBrew**.

As for running multiple php versions on one server, my choice is **Apache** with **FastCGI**.

The approach described here includes the following steps:

 - Install several php versions using **PHPBrew**
 - Install **Apache** web server with **FastCGI** module
 - Create separate **FastCGI** script for each php version
 - Map appropriate **FastCGI** script for web application execution on **virtual host level**
 
The instructions are tested on **ubuntu:xenial** docker image (Ubuntu 16.04).

Tutorial is based on setting up enviroment from scratch, so some of steps can be skipped on particular environments, however there should be no problems to execute all mentioned commands even if some packages are already installed on the system.

<div class="markdown-warning-note"><i class="fa fa-warning"></i>The installation and configuration demonstrated under <b>root</b> user for simplification. Please perform actions under appropriate user on your system where possible.</div>

# Installing all the dependencies

Adding ```multiverse``` and ```partner``` repositories to apt. These are required to fetch ```libapache2-mod-fastcgi``` package:

```
apt update
apt install software-properties-common lsb-release
add-apt-repository "deb http://archive.ubuntu.com/ubuntu $(lsb_release -sc) multiverse partner"
apt update
```

Than, we have to install MySQL, Apache and FastCGI module together with related dev packages as they will be required for PHP modules compilation:

```
apt install apache2 apache2-dev libapache2-mod-fastcgi
apt install mysql-server mysql-client libmysqlclient-dev libmysqld-dev libpq-dev
```

Ensuring all other PHP dependecies are in place:

```
apt install php php-dev php-pear autoconf automake curl libcurl3-openssl-dev build-essential libxslt1-dev re2c 
apt install libxml2 libxml2-dev php-cli bison libbz2-dev libreadline-dev libicu-dev libmcrypt-dev libmcrypt4
```

Installing PHPBrew:

```
curl -L -O https://github.com/phpbrew/phpbrew/raw/master/phpbrew
chmod +x phpbrew
mv phpbrew /usr/bin/phpbrew
phpbrew init
```

Now it is possible to install PHP 7 and 5 using PHPBrew. It will take some time.

```
phpbrew install 5.6.28 +default +dbs +apxs2 +gd +iconv +intl +mcrypt +soap
phpbrew install 7.0.13 +default +dbs +apxs2 +gd +iconv +intl +mcrypt +soap
```

Check PHPBrew [documentation](https://github.com/phpbrew/phpbrew) for further usage of various features provided by this tool.

# Configuring apache fastcgi

For editing files, you are free to use your preferred tool, or install my favourite **vim**:

```
apt install vim
```

Create a directory for FastCGI scripts:

```
mkdir /var/www/cgi-bin
```

A FastCGI script should be created for each php version.

Lets save the script for PHP 7.0.13 to ```/var/www/cgi-bin/php-7.0.13```:

```
#!/bin/sh
PHPRC="/root/.phpbrew/php/php-7.0.13/etc/"
export PHPRC

PHP_FCGI_CHILDREN=3
export PHP_FCGI_CHILDREN

PHP_FCGI_MAX_REQUESTS=5000
export PHP_FCGI_MAX_REQUESTS

exec /root/.phpbrew/php/php-7.0.13/bin/php-cgi
```

Corresponding script for PHP 5.6.28 to ```/var/www/cgi-bin/php-5.6.28```:

```
#!/bin/sh
PHPRC="/root/.phpbrew/php/php-5.6.28/etc/"
export PHPRC

PHP_FCGI_CHILDREN=3
export PHP_FCGI_CHILDREN

PHP_FCGI_MAX_REQUESTS=5000
export PHP_FCGI_MAX_REQUESTS

exec /root/.phpbrew/php/php-5.6.28/bin/php-cgi
```

Give Apache permissions to execute created scripts:

```
chmod -R +x /var/www/cgi-bin/
chown -R www-data /var/www/cgi-bin/
chmod +x /root/.phpbrew/php/php-5.6.28/bin/php-cgi
chmod +x /root/.phpbrew/php/php-7.0.13/bin/php-cgi
chown www-data /root/.phpbrew/php/php-5.6.28/bin/php-cgi
chown www-data /root/.phpbrew/php/php-7.0.13/bin/php-cgi
```

FastCGI configuration (```/etc/apache2/mods-available/fastcgi.conf```) should look like this:

```
<IfModule mod_fastcgi.c>
  AddHandler fastcgi-script .fcgi
  AddHandler php-cgi .php
  FastCgiServer /var/www/cgi-bin/php-5.6.28 -idle-timeout 3600
  FastCgiServer /var/www/cgi-bin/php-7.0.13 -idle-timeout 3600
  ScriptAlias /cgi-bin/ /var/www/cgi-bin/
</IfModule>
```

Although ScriptAlias looks odd here, it is required for proper apache rewrites handling.

**-idle-timeout** is not required, but recommended if you would like to use xdebug, for example, and do not want to get errors each time request is processing more than 30 seconds.


As FastCGI will now handle PHP files, we have to disable concurrent Apache PHP modules:

```
a2dismod php5
a2dismod php7
```

# Configuring virtual hosts

Creating basing websites:

```
mkdir /var/www/php5
mkdir /var/www/php7
echo "<?php phpinfo();" > /var/www/php5/index.php
echo "<?php phpinfo();" > /var/www/php7/index.php
chown -R www-data /var/www
```

Create **php5** website virtual host configuration (```/etc/apache2/sites-available/php5.conf```):

```
<VirtualHost *:*>
  ServerName php5.local.com
  DocumentRoot /var/www/php5
  Action php-cgi /cgi-bin/php-5.6.28
</VirtualHost>
```

Create **php7** website virtual host configuration (```/etc/apache2/sites-available/php7.conf```):

```
<VirtualHost *:*>
  ServerName php7.local.com
  DocumentRoot /var/www/php7
  Action php-cgi /cgi-bin/php-7.0.13
</VirtualHost>
```
Enable Apache actions mod to be able to handle "Action" keyword:

```
a2enmod actions
```

Enable created websites:

```
a2ensite php5.conf
a2ensite php7.conf
service apache2 restart
```

For frameworks that are using apache rewrites, such as Magento for example you might want to add the next rewrite to virtual-host configuration or .htaccess file:

```
RewriteCond %{REQUEST_URI} ^/cgi-bin/php-(.*)
RewriteRule . - [L]
```

# Testing the environment

Thats it! Now let's test the created vebsites.

As we are using custom domains, these should be added to system hosts file (```/etc/hosts```):

```
127.0.0.1   php5.local.com php7.local.com
```

Open your browser and visit php5.local.com and php7.local.com domains (or use wget).