��    *      l  ;   �      �  /   �  .   �       +     3  F  @   z     �  <   �                    2  
   :  
   E     P     \     a     n     }     �     �     �     �     �     �     �     �     �     �  t   �  G   p  ?   �     �            -        C     K     d     l  /   t  2  �  2   �  8   
     C  9   T  -  �  I   �%  
   &  ?   &     Q&     j&     n&     �&  
   �&     �&     �&     �&     �&     �&     �&     �&     �&     �&      '     '     ('     /'     A'     T'     b'  y   u'  ]   �'  T   M(     �(     �(     �(  *   �(     �(     �(  	    )     
)  /   )                         	           %                               &                               #       $          )             "          
                 *            '               (            !    12345678901 (Citizen number with eleven digits) 5301111111 (Phone number without leading zero) <span>Code</span> <span>Email, phone or citizen number</span> <table border="0" cellpadding="0" cellspacing="0" style="padding-top: 16px; background-color: #F1F1F1; font-family:Verdana, Arial,sans-serif; color: #454748; width: 100%; border-collapse:separate;"><tr><td align="center">
<table border="0" cellpadding="0" cellspacing="0" width="590" style="padding: 16px; background-color: white; color: #454748; border-collapse:separate;">
<tbody>
    <tr>
        <td align="center" style="min-width: 590px;">
            <table border="0" cellpadding="0" cellspacing="0" width="590" style="min-width: 590px; background-color: white; padding: 0px 8px 0px 8px; border-collapse:separate;">
                <tr><td valign="middle">
                    <span style="font-size: 10px;">Dear</span><br/>
                    <span style="font-size: 20px; font-weight: bold;" t-out="object.partner_id.name or ''">Marc Demo</span>
                </td><td valign="middle" align="right">
                    <img t-attf-src="/logo.png?company={{ object.company_id.id }}" style="padding: 0px; margin: 0px; height: auto; width: 80px;" t-att-alt="object.company_id.name"/>
                </td></tr>
                <tr><td colspan="2" style="text-align:center;">
                  <hr width="100%" style="background-color:rgb(204,204,204);border:medium none;clear:both;display:block;font-size:0px;min-height:1px;line-height:0; margin:16px 0px 16px 0px;"/>
                </td></tr>
            </table>
        </td>
    </tr>
    <tr>
        <td align="center" style="min-width: 590px;">
            <table border="0" cellpadding="0" cellspacing="0" width="590" style="min-width: 590px; background-color: white; padding: 0px 8px 0px 8px; border-collapse:separate;">
                <tr><td valign="top" style="font-size: 13px;">
                    <div style="text-align: center">
                        Your specially generated authentication code is<br/>
                        <h1><strong><t t-out="object.code">123456</t></strong></h1><br/>
                        Have a nice day!
                    </div>
                </td></tr>
                <tr><td style="text-align:center;">
                  <hr width="100%" style="background-color:rgb(204,204,204);border:medium none;clear:both;display:block;font-size:0px;min-height:1px;line-height:0; margin: 16px 0px 16px 0px;"/>
                </td></tr>
            </table>
        </td>
    </tr>
    <tr>
        <td align="center" style="min-width: 590px;">
            <table border="0" cellpadding="0" cellspacing="0" width="590" style="min-width: 590px; background-color: white; font-size: 11px; padding: 0px 8px 0px 8px; border-collapse:separate;">
                <tr><td valign="middle" align="left">
                    <t t-out="object.company_id.name or ''">YourCompany</t>
                </td></tr>
                <tr><td valign="middle" align="left" style="opacity: 0.7;">
                    <t t-out="object.company_id.phone or ''">+90 530-123-4567</t>
                    <t t-if="object.company_id.email">
                        | <a t-attf-href="'mailto:%s' % {{ object.company_id.email }}" style="text-decoration:none; color: #454748;" t-out="object.company_id.email or ''">info@yourcompany.com</a>
                    </t>
                    <t t-if="object.company_id.website">
                        | <a t-attf-href="'%s' % {{ object.company_id.website }}" style="text-decoration:none; color: #454748;" t-out="object.company_id.website or ''">http://www.example.com</a>
                    </t>
                </td></tr>
            </table>
        </td>
    </tr>
</tbody>
</table>
</td></tr>
</table>
             An error occured. Please contact with your system administrator. Authentication Authentication code is not correct. Please check and retype. Citizen Number: Code Code must be 6 digits Company Created by Created on Credentials Date Display Name Email Address: Error ID Language Last Modified on Last Updated by Last Updated on Next OTP Authentication OTP: Partner Partner Phone Number: Please do not share this code to anyone. Your authentication code is {{ object.code }}, expires on {{ object.date }} Please enter one of your email address, phone number or citizen number. Please enter your email address, phone number or citizen number Previous Resend Code Sign Up Time left for entering authentication code is Warning Your Authentication Code expired seconds test@test.com (Email address in regular format) Project-Id-Version: Odoo Server 15.0
Report-Msgid-Bugs-To: 
PO-Revision-Date: 2022-08-25 13:42+0300
Last-Translator: 
Language-Team: 
Language: tr
MIME-Version: 1.0
Content-Type: text/plain; charset=UTF-8
Content-Transfer-Encoding: 8bit
Plural-Forms: nplurals=2; plural=(n != 1);
X-Generator: Poedit 3.1.1
 12345678901 (Onbir haneli vatandaşlık numarası) 5301111111 (Başında sıfır olmadan telefon numarası) <span>Kod</span> <span>Eposta, telefon veya vatandaşlık numarası</span> <table border="0" cellpadding="0" cellspacing="0" style="padding-top: 16px; background-color: #F1F1F1; font-family:Verdana, Arial,sans-serif; color: #454748; width: 100%; border-collapse:separate;"><tr><td align="center">
<table border="0" cellpadding="0" cellspacing="0" width="590" style="padding: 16px; background-color: white; color: #454748; border-collapse:separate;">
<tbody>
    <tr>
        <td align="center" style="min-width: 590px;">
            <table border="0" cellpadding="0" cellspacing="0" width="590" style="min-width: 590px; background-color: white; padding: 0px 8px 0px 8px; border-collapse:separate;">
                <tr><td valign="middle">
                    <span style="font-size: 10px;">Sayın</span><br/>
                    <span style="font-size: 20px; font-weight: bold;" t-out="object.partner_id.name or ''">Marc Demo</span>
                </td><td valign="middle" align="right">
                    <img t-attf-src="/logo.png?company={{ object.company_id.id }}" style="padding: 0px; margin: 0px; height: auto; width: 80px;" t-att-alt="object.company_id.name"/>
                </td></tr>
                <tr><td colspan="2" style="text-align:center;">
                  <hr width="100%" style="background-color:rgb(204,204,204);border:medium none;clear:both;display:block;font-size:0px;min-height:1px;line-height:0; margin:16px 0px 16px 0px;"/>
                </td></tr>
            </table>
        </td>
    </tr>
    <tr>
        <td align="center" style="min-width: 590px;">
            <table border="0" cellpadding="0" cellspacing="0" width="590" style="min-width: 590px; background-color: white; padding: 0px 8px 0px 8px; border-collapse:separate;">
                <tr><td valign="top" style="font-size: 13px;">
                    <div style="text-align: center">
                        Size özel üretilen yetki kodunuz<br/>
                        <h1><strong><t t-out="object.code">123456</t></strong></h1><br/>
                        İyi günler dileriz!
                    </div>
                </td></tr>
                <tr><td style="text-align:center;">
                  <hr width="100%" style="background-color:rgb(204,204,204);border:medium none;clear:both;display:block;font-size:0px;min-height:1px;line-height:0; margin: 16px 0px 16px 0px;"/>
                </td></tr>
            </table>
        </td>
    </tr>
    <tr>
        <td align="center" style="min-width: 590px;">
            <table border="0" cellpadding="0" cellspacing="0" width="590" style="min-width: 590px; background-color: white; font-size: 11px; padding: 0px 8px 0px 8px; border-collapse:separate;">
                <tr><td valign="middle" align="left">
                    <t t-out="object.company_id.name or ''">YourCompany</t>
                </td></tr>
                <tr><td valign="middle" align="left" style="opacity: 0.7;">
                    <t t-out="object.company_id.phone or ''">+90 530-123-4567</t>
                    <t t-if="object.company_id.email">
                        | <a t-attf-href="'mailto:%s' % {{ object.company_id.email }}" style="text-decoration:none; color: #454748;" t-out="object.company_id.email or ''">info@yourcompany.com</a>
                    </t>
                    <t t-if="object.company_id.website">
                        | <a t-attf-href="'%s' % {{ object.company_id.website }}" style="text-decoration:none; color: #454748;" t-out="object.company_id.website or ''">http://www.example.com</a>
                    </t>
                </td></tr>
            </table>
        </td>
    </tr>
</tbody>
</table>
</td></tr>
</table>
             Bir hata meydana geldi. Lütfen sistem yönetimi ile iletişime geçiniz. Yetki Kodu Yetki kodu doğru değil. Lütfen kontrol edin ve tekrar girin. Vatandaşlık Numarası: Kod Yetki kodu 6 haneli olmalıdır Şirket Oluşturan Oluşturma Tarihi Bilgiler Tarih Görünen Ad Eposta Adresi: Hata ID Dil Son Düzenleme Tarihi Son Güncelleyen Son Güncelleme Tarihi İleri OTP Yetkilendirme OTP: İş Ortağı İş Ortağı Telefon Numarası: Lütfen bu kodu başka kişilerle paylaşmayınız. Yetki kodunuz {{ object.code }}, geçerlilik tarihi {{ object.date }} Lütfen eposta adresiniz, telefon numaranız veya vatandaşlık numaranızdan birini giriniz. Lütfen eposta adresiniz, telefon numaranız veya vatandaşlık numaranızı giriniz Önceki Tekrar Gönder Giriş Yetki kodunu doğrulamak için kalan süre Uyarı Yetki Kodunuz sona erdi saniye test@test.com (Düzgün formatta eposta adresi) 