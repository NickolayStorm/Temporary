import lxml.html as html
import requests


class AppealBashkortProcuracy():
    @staticmethod
    def captcha():
        page = html.parse('http://bashprok.ru/internet_reception/')
        xpath_captcha_img = '//*[@id="captcha_pic"]'
        xpath_captcha_code = '//*[@id="captcha_code"]'
        captcha_img = page.xpath(xpath_captcha_img)[0].get('src')
        captcha_code = page.xpath(xpath_captcha_code)[0].get('value')
        return {
            'url': captcha_img,
            'code': captcha_code
        }

    @staticmethod
    def send_appeal(data):
        # TODO: where is captcha data?
        pass
        # form_data = {
        #     "go": "",
        #     "try": "",
        #     "name": data["firstname"],
        #     "lastname": data["lastname"],
        #     "secondname": data["pathronymic"],
        #     "email": data["email"],
        #     "phone": "",
        #     "addr": "",
        #     "mailto": data["email"],
        #     "MAX_FILE_SIZE": 999999999,
        #     "message": ""
        # }
        # form_file = {
        #     "userfile[]": open(data["filename"], 'rb')
        # }
        # r = requests.post(url='http://bashprok.ru/include/support_form_handler.php',
        #                   data=form_data,
        #                   files=form_file)


# It is an appeal factory
def create_appeal(organisation_id):
    # Magic
    # If it is a Bashkort procuracy ->
    return AppealBashkortProcuracy