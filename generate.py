#!/usr/bin/python3

import json
from string import ascii_uppercase, ascii_lowercase
from datetime import datetime

print("Starting Macroni generator...")

output_file = open("./generated-preamble.tex", "w+")
output_file.write("""
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
%%% Macroni output file
%%% Generated {}
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
""".format(datetime.now().strftime('%Y-%m-%d %H:%M:%S')))

config_file = open("./config.json", "r")
config = json.load(config_file)

special_fonts = config['special-font-letters']

output_file.write("""
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
%%% amsmath/mathrsfs characters
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
""")

output_file.write("""
%%%--------------------------------------
%%% Fonts found in config.json:
%%%--------------------------------------
""")

for font_name in special_fonts.keys():
    font = special_fonts[font_name]
    font_command = font["command"]
    font_prefix = font["prefix"]

    output_file.write("%%% \\{}*: {} (\\{})\n".format(font_prefix, font_name,
                                                      font_command))

output_file.write("""%%%--------------------------------------
""")

for font_name in special_fonts.keys():
    font = special_fonts[font_name]
    font_prefix = font["prefix"]
    font_command = font["command"]

    output_file.write("""
%%%--------------------------------------
%%% {} characters
%%%--------------------------------------
""".format(font_name))

    # I need fromMaybe
    if "lower" in font:
        make_lowercase_macros = font["lower"]
    else:
        make_lowercase_macros = True

    if "alternative" in font:
        alternative_lowercase_chars = font["alternative"]
    else:
        alternative_lowercase_chars = []

    output_file.write("\n%%% uppercase\n\n")

    for c in ascii_uppercase:
        if c.lower() in alternative_lowercase_chars:
            output_file.write("% \\{}{} conflicts with a known LaTeX macro\n".
                              format(font_prefix, c.lower()))
            char_lower = c.lower() * 2
        else:
            char_lower = c.lower()
        output_file.write(
            "\\newcommand{{\\{prefix}{char_lower}}}{{\\{command}{{{char}}}}}\n".
            format(
                prefix=font_prefix,
                command=font_command,
                char=c,
                char_lower=char_lower))

    if make_lowercase_macros:
        output_file.write("\n%%% lowercase\n\n")
        # Macros for lowercase commands are of the form \bT and so on
        # For some reason, there are no predefined LaTeX commands of that form
        # ... yay, I guess?
        for c in ascii_lowercase:
            if False:
                pass
            else:
                output_file.write(
                    "\\newcommand{{\\{prefix}{char_upper}}}{{\\{command}{{{char}}}}}\n".
                    format(
                        prefix=font["prefix"],
                        command=font["command"],
                        char=c,
                        char_upper=c.upper()))

output_file.write("""
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
%%% topic-wise macros
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
""")
sections = config['sections']

output_file.write("\n")

for topic in sections.keys():
    topic_format = sections[topic]
    output_file.write("""
%%%--------------------------------------
%%% section \"{}\"
%%%--------------------------------------
""".format(topic))

    # Math operators

    try:
        math_operators = topic_format['math-operators']
        output_file.write("\n%%% Math operators\n\n")
        for op in math_operators.keys():
            op_data = math_operators[op]

            if "comment" in op_data:
                comment = op_data["comment"]
                if comment == "":
                    comment = "Add a comment for this"
                output_file.write("% " + comment + "\n")

            if "upper" in op_data:
                upper = op_data["upper"]
            else:
                upper = True

            if "text" in op_data:
                text = op_data["text"]
            else:
                if upper:
                    text = op.capitalize()
                else:
                    text = op

            if "custom-face" in op_data:
                output_file.write(
                    "\\newcommand{{\\{op}}}{{\\{custom_face}{{{text}}}}}\n\n"
                    .format(
                        op=op, custom_face=op_data["custom-face"], text=text))
            else:
                if "star" in op_data and op_data["star"]:
                    output_file.write(
                        "\DeclareMathOperator*{{\\{0}}}{{{1}}}\n\n".format(
                            op, text))
                else:
                    output_file.write(
                        "\DeclareMathOperator{{\\{0}}}{{{1}}}\n\n".format(
                            op, text))

    except KeyError:
        pass

    try:
        expr_aliases = topic_format['expression-aliases']
        output_file.write("%%% Aliases\n\n")
        for ncmd in expr_aliases.keys():
            ncmd_data = expr_aliases[ncmd]
            output_file.write("% {}\n".format(ncmd_data['comment']))
            output_file.write("\\newcommand{{\\{0}}}{{{1}}}\n\n".format(
                ncmd, ncmd_data['full-expr']))
    except KeyError as k:
        pass

    if "newcommands" in topic_format:
        newcommands = topic_format['newcommands']
        output_file.write('%%% newcommands\n\n')
        for ncmd in newcommands.keys():
            try:
                ncmd_data = newcommands[ncmd]
                try:
                    arity = ncmd_data['arity']
                except KeyError:
                    print(
                        "No arity provided for newcommand {}, defaulting to 1"
                        .format(ncmd))
                    arity = 1
                    config["sections"][topic]["newcommands"][ncmd]["arity"] = 1
                cmd = ncmd_data['command']
                comment = ncmd_data['comment']

                output_file.write("% {}\n".format(comment))
                output_file.write(
                    "\\newcommand{{\\{ncmd}}}[{arity}]{{{cmd}}}\n\n".format(
                        arity=arity, cmd=cmd, ncmd=ncmd))
            except KeyError as k:
                print("Error while processing newcommand {}".format(ncmd))
                print(k.__repr__())

config_file.close()
config_file = open("./config.json", "w")
json.dump(config, config_file, indent=4, sort_keys=True)
