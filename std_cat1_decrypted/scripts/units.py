# units.py
# Unit conversion — length, weight, data, speed, time, temperature.
# Pure Python math, no lookups, no internet, works offline.

from . import color_print

# All categories normalised to a base unit
LENGTH = {
    "mm": 0.001, "millimeter": 0.001, "millimetre": 0.001,
    "cm": 0.01,  "centimeter": 0.01,  "centimetre": 0.01,
    "m":  1.0,   "meter": 1.0,        "metre": 1.0,
    "km": 1000.0,"kilometer": 1000.0, "kilometre": 1000.0,
    "inch": 0.0254, "inches": 0.0254, "in": 0.0254,
    "ft": 0.3048,   "foot": 0.3048,   "feet": 0.3048,
    "yard": 0.9144, "yards": 0.9144,  "yd": 0.9144,
    "mile": 1609.344, "miles": 1609.344, "mi": 1609.344,
}

WEIGHT = {
    "mg": 0.001,   "milligram": 0.001,
    "g":  1.0,     "gram": 1.0,      "grams": 1.0,
    "kg": 1000.0,  "kilogram": 1000.0,
    "oz": 28.3495, "ounce": 28.3495, "ounces": 28.3495,
    "lb": 453.592, "lbs": 453.592,   "pound": 453.592, "pounds": 453.592,
    "tonne": 1_000_000.0, "ton": 907185.0,
}

DATA = {
    "bit": 1,  "bits": 1,
    "b":   8,  "byte": 8,    "bytes": 8,
    "kb":  8 * 1024,         "kilobyte": 8 * 1024,
    "mb":  8 * 1024**2,      "megabyte": 8 * 1024**2,
    "gb":  8 * 1024**3,      "gigabyte": 8 * 1024**3,
    "tb":  8 * 1024**4,      "terabyte": 8 * 1024**4,
}

SPEED = {
    "ms":    1.0,   "mps": 1.0,   "m/s": 1.0,
    "kmh":   1/3.6, "kph": 1/3.6, "km/h": 1/3.6,
    "mph":   0.44704,
    "knot":  0.514444, "knots": 0.514444,
    "fps":   0.3048,
}

TIME = {
    "sec": 1, "secs": 1, "second": 1, "seconds": 1, "s": 1,
    "min": 60, "mins": 60, "minute": 60, "minutes": 60,
    "hr": 3600, "hrs": 3600, "hour": 3600, "hours": 3600, "h": 3600,
    "day": 86400, "days": 86400, "d": 86400,
    "week": 604800, "weeks": 604800, "wk": 604800,
}

CATEGORIES = {
    "Length":      LENGTH,
    "Weight":      WEIGHT,
    "Data":        DATA,
    "Speed":       SPEED,
    "Time":        TIME,
}

TEMP_UNITS = {"c", "celsius", "f", "fahrenheit", "k", "kelvin"}


def _convert_temp(value, from_u, to_u):
    if from_u in ("f", "fahrenheit"):
        celsius = (value - 32) * 5 / 9
    elif from_u in ("k", "kelvin"):
        celsius = value - 273.15
    else:
        celsius = value
    if to_u in ("f", "fahrenheit"):
        return celsius * 9 / 5 + 32
    elif to_u in ("k", "kelvin"):
        return celsius + 273.15
    return celsius


def _find_unit(u):
    u = u.lower()
    if u in TEMP_UNITS:
        return "Temperature", None
    for cat_name, table in CATEGORIES.items():
        if u in table:
            return cat_name, table
    return None, None


def _fmt(value):
    if abs(value) >= 1000:
        return f"{value:,.4f}".rstrip("0").rstrip(".")
    return f"{value:.6f}".rstrip("0").rstrip(".")


def _show_all(value, from_u, cat_name, table):
    color_print.cprint(f"{value} {from_u}  —  {cat_name}", "EMPHASIS")
    if cat_name == "Temperature":
        for name in ("c", "f", "k"):
            if name != from_u:
                result = _convert_temp(value, from_u, name)
                label  = {"c": "Celsius", "f": "Fahrenheit", "k": "Kelvin"}[name]
                print(f"  {_fmt(result):>18}  {label}")
        return
    base = value * table[from_u]
    seen = set()
    for unit, factor in sorted(table.items(), key=lambda x: x[1]):
        canonical = f"{factor}"
        if canonical in seen or unit == from_u:
            continue
        seen.add(canonical)
        result = base / factor
        print(f"  {_fmt(result):>18}  {unit}")


def main(args):
    if not args or args in (["-h"], ["--help"]):
        print("""
UNITS
Usage:
  units <value> <from_unit> <to_unit> [flags]

Parameters:
  value: The number to convert
  from_unit: The unit to convert from
  to_unit: The unit to convert to. If none, shows all.

Flags:
  -h: this help section

Notes:
  Length      mm cm m km inch ft yard mile
  Weight      mg g kg oz lb tonne
  Data        bit byte kb mb gb tb
  Speed       mph kmh ms knot fps
  Time        sec min hr day week
  Temperature c f k

  I wonder. What is the purpose of imperial units?
""")
        return

    if not args[0].replace(".", "").replace("-", "").isdigit():
        color_print.cprint(f"units: '{args[0]}' is not a number.", "DARKRED")
        return

    try:
        value = float(args[0])
    except ValueError:
        color_print.cprint(f"units: invalid number '{args[0]}'", "DARKRED")
        return

    if len(args) < 2:
        color_print.cprint("units: expected a unit after the value.", "DARKRED")
        return

    from_u = args[1].lower()
    cat_name, table = _find_unit(from_u)

    if cat_name is None:
        color_print.cprint(f"units: unknown unit '{from_u}'", "DARKRED")
        return

    if len(args) == 2:
        _show_all(value, from_u, cat_name, table)
        return

    to_u = args[2].lower()
    to_cat, to_table = _find_unit(to_u)

    if to_cat is None:
        color_print.cprint(f"units: unknown unit '{to_u}'", "DARKRED")
        return

    if to_cat != cat_name:
        color_print.cprint(f"units: cannot convert {cat_name} to {to_cat}.", "DARKRED")
        return

    if cat_name == "Temperature":
        result = _convert_temp(value, from_u, to_u)
    else:
        result = (value * table[from_u]) / to_table[to_u]

    color_print.cprint(f"  {value} {from_u}  =  ", "DARKBLUE", sameline=True)
    color_print.cprint(f"{_fmt(result)} {to_u}", "EMPHASIS")