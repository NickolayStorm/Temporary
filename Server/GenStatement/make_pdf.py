import threading
import logging

import jinja2
import os
import subprocess as sp


def _as_itemize(lst: list):
    start = "\\begin{itemize}\n\\item "
    end = "\\end{itemize}"
    lst = start + \
          "\n\\item ".join(lst) \
          + end
    return lst


def _make_text(data: dict):
    # TODO: picture
    # TODO: Считывать порядок из data["order"]
    if "offence_petitions" in data:
        pp = data["offence_petitions"]
        if isinstance(pp, list):
            data["offence_petitions"] = _as_itemize(pp)
    for k, v in data.items():
        if isinstance(v, list):
            if v:
                data[k] = "\n\n".join(v)
            else:
                data[k] = ''

    template = """
        {% raw %}
\\documentclass[a4paper]{article}
\\usepackage[left=2cm,right=1cm,
             top=2cm,bottom=2cm,bindingoffset=0cm]{geometry}
\\usepackage[T2A]{fontenc}
\\usepackage[utf8]{inputenc}
\\usepackage[english,russian]{babel}
\\usepackage{hyperref}
\\usepackage{fancyhdr}
\\usepackage[export]{adjustbox}
\\usepackage{subcaption}

\\usepackage{graphicx}
% Картиночки с поворотами
\\newlength\\graphicsheight
\\newcommand{\\includegraphicsoptrotate}[2][]%
   {\\settowidth\\graphicsheight{\\includegraphics[#1]{#2'}}'%
    \\ifdim\\graphicsheight>\\textheight
      \\includegraphics[#1,height=\\linewidth,angle=90,origin=c]{#2}%
    \\else
      \\includegraphics[#1,width=\\linewidth]{#2}%
    \\fi
}
\\usepackage{placeins}
\\pagestyle{fancyplain}
\\fancyhf{}
{% endraw %}
\\lhead{ \\fancyplain{}{ № {{ request_number }} ответ прошу отправить на {{email}} } }
\\rhead{ \\fancyplain{}{\\today} }
\\cfoot{ \\fancyplain{}{\\thepage} }
 {% raw %}
\\begin{document}

  \\begin{flushright}
   {% endraw %}
  {{organization_name}}
  {% raw %}
  Отправлено через \\href{ {% endraw %} {{site}} {% raw %} }{  {% endraw %} {{site}}  {% raw %}}

  От  {% endraw %}{{user_name}} {{user_patronymic}} {{user_surname}}  {% raw %}

  Адрес для ответа в электронном виде: \\href{mailto: {% endraw %}{{email}}  {% raw %} }{ {% endraw %} {{email}}  {% raw %}}

  \\end{flushright}

  \\begin{center}

\\textbf{  {% endraw %} {{ offence }}  {% raw %} }  {% endraw %}

\\end{center}

{{problem}}

{{opinion}}

{{bases_of_excitation}}

{{offences_federal}}

{{offences_municipal}}

{{bases_of_consideration}}

На основании вышеизложенного прошу:

{{offence_petitions}}

{{problem_petitions}}

\\end{document}
        """
    template = jinja2.Template(template)

    rendered = template.render(**data).replace('_', '\_')
    return rendered


def _make_pdf(data: dict, callback: callable):
    template = _make_text(data)
    pdfdir = 'pdf'
    currnet = 'request%s' % data["request_number"]
    work_dir = os.path.join(os.curdir, pdfdir, currnet)
    if not os.path.exists(work_dir):
        os.makedirs(work_dir)
    tex_name = 'appeal.tex'
    tex_path = os.path.join(work_dir, tex_name)
    print(work_dir)
    with open(tex_path, 'w') as f:
        f.write(template)
    args = "pdflatex appeal.tex"
    print(args)
    subprocess = sp.Popen(args,
                          cwd=work_dir)
    try:
        subprocess.wait(1)
        return callback(os.path.join(work_dir, 'appeal.pdf'))
    except TimeoutError:
        logging.error("Cannot create request %s" % data["request_number"])
        return False
    except FileNotFoundError:
        logging.error("Cannot create request %s:"
                      " please make sure you have 'pdflatex' util" % data["request_number"])
        return False


def make_pdf(data, callback):
    _make_pdf(data, callback)
    # t = threading.Thread(target=_make_pdf, args=(data, callback, ))
    # t.start()
    # return True
