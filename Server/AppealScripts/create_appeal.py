import lxml.html as html
import requests


class AppealBashkortProcuracy:
    @staticmethod
    def captcha():
        page = html.parse('http://bashprok.ru/internet_reception/')
        xpath_captcha_img = '//*[@id="captcha_pic"]'
        xpath_captcha_code = '//*[@id="captcha_code"]'
        captcha_img = page.xpath(xpath_captcha_img)[0].get('src')
        captcha_code = page.xpath(xpath_captcha_code)[0].get('value')
        return {
            'url': 'http://bashprok.ru' + captcha_img,
            'code': captcha_code
        }

    # Should return callable
    @staticmethod
    def send_appeal(data: dict) -> callable:
        def send_data(pdf_path):
            form_data = {
                "go": "",
                "try": "",
                "name": data["firstname"],
                "lastname": data["lastname"],
                "secondname": data["pathronymic"],
                "email": data["email"],
                "phone": "",
                "addr": "",
                "mailto": data["email"],
                "MAX_FILE_SIZE": 999999999,
                "message": ""
            }
            with open(pdf_path, 'rb') as f:
                form_file = {
                    "userfile[]": f
                }
                # r = requests.post(url='http://bashprok.ru/include/support_form_handler.php',
                #                   data=form_data,
                #                   files=form_file)
        return send_data


# It is an appeal factory
def create_appeal(organisation_id):
    # Magic
    # If it is a Bashkort procuracy ->
    return AppealBashkortProcuracy
