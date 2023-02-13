# from ptpython.repl import embed, run_config, PythonRepl
from IPython import embed

# def default_configure(repl: PythonRepl):
#     """
#     Default REPL configuration function
#     :param repl:
#     :return:
#     """
#     repl.show_signature = True
#     repl.show_docstring = True
#     repl.show_status_bar = True
#     repl.show_sidebar_help = True
#     repl.highlight_matching_parenthesis = True
#     repl.wrap_lines = True
#     repl.complete_while_typing = True
#     repl.vi_mode = False
#     repl.paste_mode = False
#     repl.prompt_style = 'classic'  # 'classic' or 'ipython'
#     repl.insert_blank_line_after_output = False
#     repl.enable_history_search = False
#     repl.enable_auto_suggest = False
#     repl.enable_open_in_editor = True
#     repl.enable_system_bindings = False
#     repl.confirm_exit = True
#     repl.enable_input_validation = True

# async def start_repl(loop, globals):
#     configure = default_configure
#     await embed(
#         globals=globals,
#         title='AutoBahn-Python REPL',
#         return_asyncio_coroutine=True,
#         patch_stdout=True,
#         configure=configure
#     )

async def start_repl(loop, globals):
    embed(using='asyncio', user_ns=globals)