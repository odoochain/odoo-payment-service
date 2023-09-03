**JetCheckout**

JetCheckout is an online payment platform designed for corporate
businesses.

**Payment Service**

Payment Service is an open source part of JetCheckout Platform that
offers whitelabel functionality. You can create your own online payment
brand.

You can join and follow the news and announcements from Telegram group
below.

[*https://t.me/+U6V29rMrOZNkYTk8*](https://t.me/+U6V29rMrOZNkYTk8)

![](media/image1.png){width="2.285589457567804in"
height="2.2817924321959757in"}

**Functions & Scope**

1\. Integrated Payment Systems in Turkey

Paynet | PayTR | Iyzico | OzanPAY

2\. Integrated Virtual POS Systems in Turkey

Akbank |Alternatifbank | Fibabanka | Halkbank | INGBank | Odeabank |
Şekerbank | HSBC | TEB | İş Bankası | Ziraat | Garanti BBVA | Yapı Kredi
QNB Finansbank | Vakıfbank | Denizbank | Albaraka | Anadolu Bank |
Kuveyt Türk | Türkiye Finans

3\. Independent and Login-Free Payment Page

4\. Dynamic Lowest Cost Transaction Routing Between Integrated Systems

5\. Focused Vertical Solutions Specially Produced For Sectoral Needs

Customer Payments | Dealer Payments | Field Sales Payments | Student
Payments

**Installation & Configuration Guide**

You can run “JetCheckout Payment Service Platform” on your own server.

1\. Step : Install Odoo as a Business Platform

Here is the guide that you need to install Odoo as a business platform.

[*https://www.odoo.com/documentation/15.0/administration/install.html*](https://www.odoo.com/documentation/15.0/administration/install.html)

2\. Step : Add Payment Service Modules To The Business Platform

**Git:** The following requires https://git-scm.com to be installed on
your machine and that you have basic knowledge of git commands.

-   git clone git@github.com:projetgrup/payment-service.git

Navigate to the path of your payment-service addons path and run
**pip3** on the requirements file in a terminal **with root
privileges**:

-   pip3 install setuptools wheel

-   pip3 install -r requirements.txt

Now you have to add the "payment-service" path in the "odoo config" file
and restart odoo service.

-   nano /etc/odoo/odoo.conf

-   addons\_path = /../../odoo/addons, &lt;payment-service-path&gt;

Once you finished the process restart the server to configure the file.

You can use the following command to restart the server to configure the
file.

-   sudo service odoo restart

3 Step : Available Addons

  **Addon**                    **Summary**
  ---------------------------- -------------
  whitelabel                   
  payment\_jetcheckout         
  payment\_jetcheckout\_page   
  payment\_student             
  payment\_student\_rest       
  base\_rest                   
  base\_rest\_datamodel        
  component                    
  datamodel                    

3.1 Step : Install Payment Service Modules and Run Your Own Business

![](media/image2.gif){width="6.805369641294838in"
height="5.101148293963255in"}

4\. Step : Create Your JetCheckout Account and Connect It To Your Own
Business

Create a JetCheckout account from the link below.

[*https://www.jetcheckout.com/web/signup*](https://www.jetcheckout.com/web/signup)

If you have any problems, report it to the e-mail address below.

jetcheckout@projetgrup.com

**Developer Tutorials**

Don't limit your imagination!

-   Create your own brand

-   Develop your own modules on a stable platform

-   Develop vertical solutions, create new markets for yourself

Here is the guide that you need to develop your own modules as addons

[*https://www.odoo.com/documentation/15.0/developer/howtos.html*](https://www.odoo.com/documentation/15.0/developer/howtos.html)
