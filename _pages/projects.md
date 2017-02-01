---
layout: page
title: My Projects
permalink: /projects/
meta_description: Sergii Ivashchenko open source projects. Free utilities, libraries and Magento 2 extensions.
tags: projects
---

<div class="project-container clearfix">
    <div class="project-thumb-block">
        <a href="//www.packtpub.com/web-development/mastering-magento-2-video">
            <img src="{{ site.url }}/images/mastering-magento-2.jpg" alt="Mastering Magento 2 Video Course" class="project-thumb"/>
        </a>
    </div>
    <div class="project-description-block">
        <h3 class="project-name">Mastering Magento 2 Video Course</h3>
        <div class="project-description">
            Video course concentrating best practices and approaches of Magento 2 extensions implementation.
        </div>
        <div class="project-link">More on <a href="//www.packtpub.com/web-development/mastering-magento-2-video">PacktPub</a></div>
    </div>
</div>
<div class="project-container clearfix">
    <div class="project-thumb-block">
        <a href="//github.com/sivaschenko/utility-cron">
            <img src="{{ site.url }}/images/project-utility-cron.png" alt="PHP Cron Library" class="project-thumb"/>
        </a>
    </div>
    <div class="project-description-block">
        <h3 class="project-name">PHP Cron Library</h3>
        <div class="project-description">
            The PHP Cron Library can be used to get human readable cron expression description and detailed validation messages.
        </div>
        <div class="project-link">More on <a href="//github.com/sivaschenko/utility-cron">Github</a></div>
    </div>
</div>
{% if site.show_donation_block %}
<hr/>
You can endorse my posts and projects using button underneath.
<form action="https://www.paypal.com/cgi-bin/webscr" method="post" target="_top">
<input type="hidden" name="cmd" value="_s-xclick">
<input type="hidden" name="hosted_button_id" value="22PRKX7R383WA">
<input type="image" src="https://www.paypalobjects.com/en_US/i/btn/btn_donate_LG.gif" border="0" name="submit" alt="PayPal - The safer, easier way to pay online!">
<img alt="" border="0" src="https://www.paypalobjects.com/en_US/i/scr/pixel.gif" width="1" height="1">
</form>
{% endif %}
