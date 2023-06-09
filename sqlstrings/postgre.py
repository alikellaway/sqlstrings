from sqlstrings.value_handling import write_val
import logging
from typing import Any

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


def insert(table_name: str, names_values: dict[str:str] | list[dict[str:str]]) -> str:
    """
    Generates an insert statement for a postgre sql database.
    :param table_name: The name of the table to insert into.
    :param names_values: A dictionary or list of dictionaries with names of the columns and the values mapped to each column.
    :return: A string insert statement able to insert the given information.
    """
    outstr = f'INSERT INTO {table_name}\n'
    def args_serialise(value_dict): return ", ".join(
        map(lambda v: {write_val(v)}, value_dict.values()))
    if isinstance(names_values, list):
        names = names_values[0].keys()
        values_str = ", \n\t".join(
            map(lambda d: f'({args_serialise(d)})', names_values))
    elif isinstance(names_values, dict):
        names = names_values.keys()
        values_str = f'({args_serialise(names_values)})'
    names_str = ", ".join(map(lambda n: f'{n}', names))
    outstr += f'\t{table_name}({names_str})\nVALUES\n\t{values_str};'
    logging.debug(f'Created {__name__} insertion:\n{outstr}')
    return outstr


def update(table_name: str, names_values: dict[str:str], where: str = None) -> str:
    """
    Generates an update statement for a postgre sql database.
    :param table_name: The name of the table to update.
    :param names_values: A dict mapping the names of the columns to update to the values to update them to.
    :param where: A string of conditionals which will be used to filter the tuples to update.
    :return: A string that can be used to update the table <table_name> with the values given in a postgre db.
    """
    outstr = f'UPDATE {table_name}\nSET '
    outstr += ",\n    ".join(
        map(lambda kvp: f'{kvp[0]} = {write_val(kvp[1])}', names_values.items()))
    if where is not None:
        outstr += f'\nWHERE {where};'
    logger.debug(f'Created {__name__} update:\n{outstr}')
    return outstr


def create_table(table_name: str, names_types: dict[str:str]) -> str:
    """
    Generates a string that can be used to create a table of the given name and types when the string is executed.
    :param table_name: The name of the table to create.
    :param names_types: A dictionary mapping the field names to the field types.
    :return: A string that can be used to create tables in a sql database.
    """
    outstr = f'CREATE TABLE {table_name} ('
    outstr += ",\n\t".join(
        map(lambda kvp: f'{kvp[0]} {kvp[1]}', names_types.items())) + "\n);"
    logger.debug(f'Created {__name__} table creator:\n{outstr}')
    return outstr


def procedure_call(proc_name: str, param_args: dict[str:Any]) -> str:
    """
    Generates a string that can be used to call a procedure of a given name with the given arguments when executed.
    :param proc_name: The name of the procedure to call.
    :param param_args: The names of the parameters mapped to their respective values.
    """
    outstr = f'CALL {proc_name}({", ".join(map(lambda kvp: write_val(kvp[1]), param_args.items()))});'
    logging.debug(f'Created {__name__} proceduce call:\n{outstr}')
    return outstr


def drop_table(table_names: str | list, if_exists: bool = False, cascade: bool = False, restrict: bool = False) -> str:
    """
    Generates a string that can be used to drop a table given its name (or multiple tables when given a list of names) when executed.
    :param table_names: The name or list of names of table(s) to drop. NOTE: You cannot add cascade and restrict to the same string.
    :param if_exists: Whether to add if exists to the string.
    :param cascade: Whether to add CASCADE to the string.
    :param restrict: Whether to add RESTRICT to the string.
    :return: A string that can be used to drop tables from sql databases.
    """
    outstr = f'DROP TABLE '
    outstr += " IF EXISTS  " if if_exists else ""
    outstr += table_names if isinstance(table_names,
                                        str) else ", ".join(table_names)
    outstr += " CASCADE" if cascade and not restrict else ""
    outstr += " RESTRICT" if restrict and not cascade else ""
    return outstr + ";"


def select(cols: str | tuple[str], frm: str, distinct: bool = False, where: str = None, group_by: str | tuple[str] = None, having: str = None, order_by: str | tuple[str] = None, order_desc: bool = False, limit: int = None, offset: int = None, fetch: int = None) -> str:
    """
    Generates postgre select statements given parameters.
    :param cols: The names of the columns to retrieve.
    :param frm: Where we are selecting from.
    :param distinct: Whether the results should be distinct.
    :param where: The conditional to filter results.
    :param group_by: The names of columns to group by.
    :param having: The conditional to filter groups.
    :param order_by: The names of the columns to order resuts on.
    :param order_desc: Whether the results should be ordered in descending order (default asc).
    :param limit: The argument to the LIMIT keyword.
    :param offset: The argument to the OFFSET keyword.
    :param fetch: The argument to the FETCH keyword.
    :return: A string that can be used to select entries from a sql server.
    """
    # Select
    cols = tuple(cols) if isinstance(cols, str) else cols
    outstr = f"SELECT {'DISTINCT ' if distinct else ''}{', '.join(cols)}"
    # From
    outstr += f'\nFROM {frm}'
    # Where
    outstr += "" if where is None else f'\nWHERE {where}'
    # Group by
    if group_by is not None:
        group_by = tuple(group_by) if isinstance(group_by, str) else group_by
        outstr += f'\nGROUP BY {", ".join(group_by)}'
    # Having
    outstr += "" if having is None else f'\nHAVING {having}'
    # Order by
    if order_by is not None:
        order_by = tuple(order_by) if isinstance(order_by, str) else order_by
        outstr += f'\nORDER BY {", ".join(order_by)}{"" if not order_desc else " DESC"}'
    elif order_desc:
        outstr += f'\nORDER BY DESC'
    # Limit
    outstr += "" if limit is None else f'\nLIMIT {limit}'
    # Offset
    outstr += "" if offset is None else f'\nOFFSET {offset} ROWS'
    # Fetch
    outstr += "" if fetch is None else f'\nFETCH FIRST {fetch} ROWS ONLY'
    return outstr + ";"


if __name__ == '__main__':
    d = {
        "contact_id": "id1",
        "name": "name1",
        "sname": "sname1"
    }
    dl = [d, d, d, d]
    # print(update("table1", d))
    # print(insertion("table2", d))
    # print(procedure_call("proc_name", d))
    # print(create_table("table1", d))
    # print(drop_table(["table", "table2", "table3"]))
    print(select(['name', 'age'], "table_name", order_desc=True))
