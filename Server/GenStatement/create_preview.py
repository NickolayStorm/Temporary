def create_preview(data: dict, request_number: int):
    text = '<html><head><meta charset="utf-8">'
    text += '<title>Обращение №%s</title>' % request_number
    text += '</head><body>'
    for x in data['offences']:
        text += '<h4>%s</h4>' % x
    if data.get('problem'):
        text += '<p>%s</p>' % data['problem']
    if data.get('options'):
        for x in data['options']:
            text += '<p>%s</p>' % x
    if data.get('bases_of_excitation'):
        for x in data['bases_of_excitation']:
            text += '<p>%s</p>' % x
    if data.get('offences_federal'):
        for x in data['offences_federal']:
            text += '<p>%s</p>' % x
    if data.get('offences_municipal'):
        for x in data['offences_municipal']:
            text += '<p>%s</p>' % x
    if data.get('bases_of_consideration'):
        for x in data['bases_of_consideration']:
            text += '<p>%s</p>' % x
    text += '<p>На основании вышеизложенного прошу:</p>'
    if data.get('offence_petitions'):
        text += '<ol>'
        for x in data['offence_petitions']:
            text += '<li>%s</li>' % x
        text += '</ol>'
    if data.get('problem_petitions'):
        text += '<ol>'
        for x in data['problem_petitions']:
            text += '<li>%s</li>' % x
        text += '</ol>'
    text += '</body></html>'

    with open('/home/activebash/preview/%s.html' % request_number, 'wt') as out:
        out.write(text)
    return 'https://gorodovojbot.ru:8443/preview/%s.html' % request_number
