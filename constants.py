# constants.py
import random

# ============== DATY ==============
START_YEAR_MIN = 1492
START_YEAR_MAX = 1776

def generate_start_date():
    from datetime import datetime
    year = random.randint(START_YEAR_MIN, START_YEAR_MAX)
    month = random.randint(1, 12)
    day = random.randint(1, 28)
    return datetime(year, month, day)

# constants.py
MAX_SHIP_CARGO = 1500

# ============== PAŃSTWA ==============
STATES = {
    "Portugalia": {
        "bonus": "szybsze statki", "speed": 1.3,
        "rulers": [
            {"name": "Jan II Doskonały", "start": 1481, "end": 1495},
            {"name": "Manuel I Szczęśliwy", "start": 1495, "end": 1521},
            {"name": "Jan III", "start": 1521, "end": 1557},
            {"name": "Sebastian I", "start": 1557, "end": 1578},
            {"name": "Henryk I Kardynał", "start": 1578, "end": 1580},
            {"name": "Antoni I", "start": 1580, "end": 1580},
            {"name": "Filip I", "start": 1580, "end": 1598},
            {"name": "Filip II", "start": 1598, "end": 1621},
            {"name": "Jan IV Bragança", "start": 1640, "end": 1656},
            {"name": "Alfons VI", "start": 1656, "end": 1683},
            {"name": "Piotr II", "start": 1683, "end": 1706},
            {"name": "Jan V", "start": 1706, "end": 1750},
            {"name": "Józef I Reformator", "start": 1750, "end": 1777},
            {"name": "Maria I", "start": 1777, "end": 1816}
        ]
    },
    "Hiszpania": {
        "bonus": "lepsza eksploracja", "explore": 1.4,
        "rulers": [
            {"name": "Izabela I Kastylijska", "start": 1474, "end": 1504},
            {"name": "Ferdynand II Aragoński", "start": 1479, "end": 1516},
            {"name": "Joanna Szalona", "start": 1504, "end": 1555},
            {"name": "Karol I", "start": 1516, "end": 1556},
            {"name": "Filip II", "start": 1556, "end": 1598},
            {"name": "Filip III", "start": 1598, "end": 1621},
            {"name": "Filip IV", "start": 1621, "end": 1665},
            {"name": "Karol II", "start": 1665, "end": 1700},
            {"name": "Filip V Burbon", "start": 1700, "end": 1746},
            {"name": "Ferdynand VI", "start": 1746, "end": 1759},
            {"name": "Karol III", "start": 1759, "end": 1788},
            {"name": "Karol IV", "start": 1788, "end": 1808}
        ]
    },
    "Anglia": {
        "bonus": "lepszy handel", "trade": 1.3,
        "rulers": [
            {"name": "Henryk VII Tudor", "start": 1485, "end": 1509},
            {"name": "Henryk VIII", "start": 1509, "end": 1547},
            {"name": "Edward VI", "start": 1547, "end": 1553},
            {"name": "Maria I Krwawa", "start": 1553, "end": 1558},
            {"name": "Elżbieta I", "start": 1558, "end": 1603},
            {"name": "Jakub I Stuart", "start": 1603, "end": 1625},
            {"name": "Karol I", "start": 1625, "end": 1649},
            {"name": "Oliver Cromwell (Lord Protektor)", "start": 1653, "end": 1658},
            {"name": "Ryszard Cromwell", "start": 1658, "end": 1659},
            {"name": "Karol II", "start": 1660, "end": 1685},
            {"name": "Jakub II", "start": 1685, "end": 1688},
            {"name": "Wilhelm III Orański i Maria II", "start": 1689, "end": 1702},
            {"name": "Anna Stuart", "start": 1702, "end": 1714},
            {"name": "Jerzy I Hanowerski", "start": 1714, "end": 1727},
            {"name": "Jerzy II", "start": 1727, "end": 1760},
            {"name": "Jerzy III", "start": 1760, "end": 1820}
        ]
    },
    "Francja": {
        "bonus": "lepsza dyplomacja", "diplo_bonus": 15,
        "rulers": [
            {"name": "Karol VIII", "start": 1483, "end": 1498},
            {"name": "Ludwik XII", "start": 1498, "end": 1515},
            {"name": "Franciszek I", "start": 1515, "end": 1547},
            {"name": "Henryk II", "start": 1547, "end": 1559},
            {"name": "Franciszek II", "start": 1559, "end": 1560},
            {"name": "Karol IX", "start": 1560, "end": 1574},
            {"name": "Henryk III", "start": 1574, "end": 1589},
            {"name": "Henryk IV Burbon", "start": 1589, "end": 1610},
            {"name": "Ludwik XIII", "start": 1610, "end": 1643},
            {"name": "Ludwik XIV Król Słońce", "start": 1643, "end": 1715},
            {"name": "Ludwik XV", "start": 1715, "end": 1774},
            {"name": "Ludwik XVI", "start": 1774, "end": 1792}
        ]
    },
    "Holandia": {
        "bonus": "taniej budować", "build_cost": 0.8,
        "rulers": [
            {"name": "Filip II", "start": 1555, "end": 1581},
            {"name": "Rada Stanu", "start": 1581, "end": 1588},
            {"name": "Maurycy Orański", "start": 1585, "end": 1625},
            {"name": "Fryderyk Henryk Orański", "start": 1625, "end": 1647},
            {"name": "Wilhelm II Orański", "start": 1647, "end": 1650},
            {"name": "Okres bez stadhoudera (I)", "start": 1650, "end": 1672},
            {"name": "Wilhelm III Orański", "start": 1672, "end": 1702},
            {"name": "Okres bez stadhoudera (II)", "start": 1702, "end": 1747},
            {"name": "Wilhelm IV Orański", "start": 1747, "end": 1751},
            {"name": "Wilhelm V Orański", "start": 1751, "end": 1795}
        ]
    },
    "Szwecja": {
        "bonus": "lepsza produkcja drewna", "wood": 1.5,
        "rulers": [
            {"name": "Sten Starszy", "start": 1470, "end": 1497},
            {"name": "Jan Oldenburński", "start": 1497, "end": 1501},
            {"name": "Sten Sture Młodszy", "start": 1512, "end": 1520},
            {"name": "Krystian II", "start": 1520, "end": 1521},
            {"name": "Gustaw I Waza", "start": 1523, "end": 1560},
            {"name": "Erik XIV", "start": 1560, "end": 1568},
            {"name": "Jan III", "start": 1568, "end": 1592},
            {"name": "Zygmunt III Waza", "start": 1592, "end": 1599},
            {"name": "Karol IX", "start": 1599, "end": 1611},
            {"name": "Gustaw II Adolf", "start": 1611, "end": 1632},
            {"name": "Krystyna", "start": 1632, "end": 1654},
            {"name": "Karol X Gustaw", "start": 1654, "end": 1660},
            {"name": "Karol XI", "start": 1660, "end": 1697},
            {"name": "Karol XII", "start": 1697, "end": 1718},
            {"name": "Ulryka Eleonora", "start": 1718, "end": 1720},
            {"name": "Fryderyk I", "start": 1720, "end": 1751},
            {"name": "Adolf Fryderyk", "start": 1751, "end": 1771},
            {"name": "Gustaw III", "start": 1771, "end": 1792},
            {"name": "Gustaw IV Adolf", "start": 1792, "end": 1809}
        ]
    },
    "Dania": {
        "bonus": "lepsza żywność", "food": 1.4,
        "rulers": [
            {"name": "Jan Oldenburński", "start": 1481, "end": 1513},
            {"name": "Krystian II", "start": 1513, "end": 1523},
            {"name": "Fryderyk I", "start": 1523, "end": 1533},
            {"name": "Krystian III", "start": 1534, "end": 1559},
            {"name": "Fryderyk II", "start": 1559, "end": 1588},
            {"name": "Krystian IV", "start": 1588, "end": 1648},
            {"name": "Fryderyk III", "start": 1648, "end": 1670},
            {"name": "Krystian V", "start": 1670, "end": 1699},
            {"name": "Fryderyk IV", "start": 1699, "end": 1730},
            {"name": "Krystian VI", "start": 1730, "end": 1746},
            {"name": "Fryderyk V", "start": 1746, "end": 1766},
            {"name": "Krystian VII", "start": 1766, "end": 1808}
        ]
    },
    "Wenecja": {
        "bonus": "lepszy handel", "trade": 1.5,
        "rulers": [
            {"name": "Agostino Barbarigo", "start": 1486, "end": 1501},
            {"name": "Leonardo Loredan", "start": 1501, "end": 1521},
            {"name": "Antonio Grimani", "start": 1521, "end": 1523},
            {"name": "Andrea Gritti", "start": 1523, "end": 1538},
            {"name": "Pietro Lando", "start": 1538, "end": 1545},
            {"name": "Francesco Donato", "start": 1545, "end": 1553},
            {"name": "Marcantonio Trivisan", "start": 1553, "end": 1554},
            {"name": "Francesco Venier", "start": 1554, "end": 1556},
            {"name": "Lorenzo Priuli", "start": 1556, "end": 1559},
            {"name": "Girolamo Priuli", "start": 1559, "end": 1567},
            {"name": "Pietro Loredan", "start": 1567, "end": 1570},
            {"name": "Alvise I Mocenigo", "start": 1570, "end": 1577},
            {"name": "Sebastiano Venier", "start": 1577, "end": 1578},
            {"name": "Nicolò da Ponte", "start": 1578, "end": 1585},
            {"name": "Pasquale Cicogna", "start": 1585, "end": 1595},
            {"name": "Marino Grimani", "start": 1595, "end": 1605},
            {"name": "Leonardo Donato", "start": 1606, "end": 1612},
            {"name": "Marcantonio Memmo", "start": 1612, "end": 1615},
            {"name": "Giovanni Bembo", "start": 1615, "end": 1618},
            {"name": "Nicolò Donato", "start": 1618, "end": 1618},
            {"name": "Antonio Priuli", "start": 1618, "end": 1623},
            {"name": "Francesco Contarini", "start": 1623, "end": 1624},
            {"name": "Giovanni I Cornaro", "start": 1625, "end": 1629},
            {"name": "Nicolò Contarini", "start": 1630, "end": 1631},
            {"name": "Francesco Erizzo", "start": 1631, "end": 1646},
            {"name": "Francesco Molin", "start": 1646, "end": 1655},
            {"name": "Carlo Contarini", "start": 1655, "end": 1656},
            {"name": "Francesco Cornaro", "start": 1656, "end": 1656},
            {"name": "Bertuccio Valier", "start": 1656, "end": 1658},
            {"name": "Giovanni Pesaro", "start": 1658, "end": 1659},
            {"name": "Domenico II Contarini", "start": 1659, "end": 1675},
            {"name": "Nicolò Sagredo", "start": 1675, "end": 1676},
            {"name": "Alvise Contarini", "start": 1676, "end": 1684},
            {"name": "Marcantonio Giustinian", "start": 1684, "end": 1688},
            {"name": "Francesco Morosini", "start": 1688, "end": 1694},
            {"name": "Sylwester Valier", "start": 1694, "end": 1700},
            {"name": "Alvise II Mocenigo", "start": 1700, "end": 1709},
            {"name": "Giovanni II Cornaro", "start": 1709, "end": 1722},
            {"name": "Alvise III Mocenigo", "start": 1722, "end": 1732},
            {"name": "Carlo Ruzzini", "start": 1732, "end": 1735},
            {"name": "Alvise Pisani", "start": 1735, "end": 1741},
            {"name": "Pietro Grimani", "start": 1741, "end": 1752},
            {"name": "Francesco Loredan", "start": 1752, "end": 1762},
            {"name": "Marco Foscarini", "start": 1762, "end": 1763},
            {"name": "Alvise IV Mocenigo", "start": 1763, "end": 1779},
            {"name": "Paolo Renier", "start": 1779, "end": 1789},
            {"name": "Ludovico Manin", "start": 1789, "end": 1797}
        ]
    },
    "Genua": {
        "bonus": "bogate kopalnie", "mine": 1.4,
        "rulers": [
            {"name": "Battista Fregoso", "start": 1478, "end": 1483},
            {"name": "Paolo Fregoso", "start": 1483, "end": 1488},
            {"name": "Ludwik XII Francji", "start": 1499, "end": 1512},
            {"name": "Ottaviano Fregoso", "start": 1513, "end": 1515},
            {"name": "Antoni Adorno", "start": 1522, "end": 1527},
            {"name": "Teodoro Trivulzio", "start": 1528, "end": 1531},
            {"name": "Andrea Doria (nieformalny)", "start": 1528, "end": 1560},
            {"name": "Giovanni Battista Lascaris", "start": 1561, "end": 1573},
            {"name": "Gianandrea Giustiniani", "start": 1573, "end": 1575},
            {"name": "Ambrogio Di Negro", "start": 1581, "end": 1583},
            {"name": "Giovanni Battista Cattaneo", "start": 1607, "end": 1609},
            {"name": "Giulio Della Torre", "start": 1611, "end": 1613},
            {"name": "Pietro De Franchi", "start": 1621, "end": 1623},
            {"name": "Federico De Franchi", "start": 1623, "end": 1625},
            {"name": "Giovanni Luca Chiavari", "start": 1627, "end": 1629},
            {"name": "Andrea Spinola", "start": 1629, "end": 1631},
            {"name": "Leonardo Della Torre", "start": 1631, "end": 1633},
            {"name": "Giovanni Francesco Brignole", "start": 1635, "end": 1637},
            {"name": "Agostino Pallavicini", "start": 1637, "end": 1639},
            {"name": "Giovanni Battista Durazzo", "start": 1675, "end": 1677},
            {"name": "Francesco Maria Imperiale", "start": 1715, "end": 1717},
            {"name": "Giuseppe Maria Imperiale", "start": 1727, "end": 1729},
            {"name": "Domenico Invrea", "start": 1761, "end": 1763},
            {"name": "Rodolfo Emilio Brignole", "start": 1787, "end": 1789},
            {"name": "Alviso Lomellini", "start": 1791, "end": 1793},
            {"name": "Giacomo Maria Brignole", "start": 1795, "end": 1797}
        ]
    },
    "Polska": {
        "bonus": "dużo ludzi", "pop_start": 20,
        "rulers": [
            {"name": "Kazimierz IV Jagiellończyk", "start": 1447, "end": 1492},
            {"name": "Jan I Olbracht", "start": 1492, "end": 1501},
            {"name": "Aleksander Jagiellończyk", "start": 1501, "end": 1506},
            {"name": "Zygmunt I Stary", "start": 1506, "end": 1548},
            {"name": "Zygmunt II August", "start": 1548, "end": 1572},
            {"name": "Henryk Walezy", "start": 1573, "end": 1574},
            {"name": "Stefan Batory", "start": 1576, "end": 1586},
            {"name": "Zygmunt III Waza", "start": 1587, "end": 1632},
            {"name": "Władysław IV Waza", "start": 1632, "end": 1648},
            {"name": "Jan II Kazimierz Waza", "start": 1648, "end": 1668},
            {"name": "Michał Korybut Wiśniowiecki", "start": 1669, "end": 1673},
            {"name": "Jan III Sobieski", "start": 1674, "end": 1696},
            {"name": "August II Mocny", "start": 1697, "end": 1706},
            {"name": "Stanisław Leszczyński", "start": 1704, "end": 1709},
            {"name": "August II Mocny", "start": 1709, "end": 1733},
            {"name": "Stanisław Leszczyński", "start": 1733, "end": 1736},
            {"name": "August III Sas", "start": 1733, "end": 1763},
            {"name": "Stanisław August Poniatowski", "start": 1764, "end": 1795}
        ]
    },
    "Szkocja": {
        "bonus": "odporni na choroby", "health": 1.5,
        "rulers": [
            {"name": "Jakub III", "start": 1460, "end": 1488},
            {"name": "Jakub IV", "start": 1488, "end": 1513},
            {"name": "Jakub V", "start": 1513, "end": 1542},
            {"name": "Maria Stuart", "start": 1542, "end": 1567},
            {"name": "Jakub VI", "start": 1567, "end": 1625},
            {"name": "Karol I", "start": 1625, "end": 1649},
            {"name": "Karol II", "start": 1649, "end": 1685},
            {"name": "Jakub VII", "start": 1685, "end": 1688},
            {"name": "Maria II i Wilhelm III", "start": 1689, "end": 1702},
            {"name": "Anna", "start": 1702, "end": 1707}
        ]
    },
    "Neapol": {
        "bonus": "szybkie plantacje", "plantation": 1.4,
        "rulers": [
            {"name": "Ferdynand I", "start": 1458, "end": 1494},
            {"name": "Alfons II", "start": 1494, "end": 1495},
            {"name": "Ferdynand II", "start": 1495, "end": 1496},
            {"name": "Fryderyk I", "start": 1496, "end": 1501},
            {"name": "Ludwik XII Francji", "start": 1501, "end": 1504},
            {"name": "Ferdynand III Aragoński", "start": 1504, "end": 1516},
            {"name": "Joanna III", "start": 1516, "end": 1555},
            {"name": "Karol V", "start": 1516, "end": 1556},
            {"name": "Filip I", "start": 1556, "end": 1598},
            {"name": "Filip II", "start": 1598, "end": 1621},
            {"name": "Filip III", "start": 1621, "end": 1665},
            {"name": "Karol II Hiszpański", "start": 1665, "end": 1700},
            {"name": "Filip IV", "start": 1700, "end": 1707},
            {"name": "Karol VI Habsburg", "start": 1707, "end": 1734},
            {"name": "Karol VII Burbon", "start": 1734, "end": 1759},
            {"name": "Ferdynand IV", "start": 1759, "end": 1799}
        ]
    },
    "Aragonia": {
        "bonus": "lepsza marynarka", "ships": 1.3,
        "rulers": [
            {"name": "Jan II", "start": 1458, "end": 1479},
            {"name": "Ferdynand II", "start": 1479, "end": 1516},
            {"name": "Joanna Szalona", "start": 1516, "end": 1555},
            {"name": "Karol I", "start": 1516, "end": 1556},
            {"name": "Filip II", "start": 1556, "end": 1598},
            {"name": "Filip III", "start": 1598, "end": 1621},
            {"name": "Filip IV", "start": 1621, "end": 1665},
            {"name": "Karol II", "start": 1665, "end": 1700},
            {"name": "Filip V", "start": 1700, "end": 1746},
            {"name": "Ferdynand VI", "start": 1746, "end": 1759},
            {"name": "Karol III", "start": 1759, "end": 1788},
            {"name": "Karol IV", "start": 1788, "end": 1808}
        ]
    },
    "Kastylia": {
        "bonus": "dużo złota", "gold_find": 1.6,
        "rulers": [
            {"name": "Jan II", "start": 1406, "end": 1454},
            {"name": "Henryk IV", "start": 1454, "end": 1474},
            {"name": "Izabela I", "start": 1474, "end": 1504},
            {"name": "Joanna Szalona", "start": 1504, "end": 1555},
            {"name": "Karol I", "start": 1516, "end": 1556},
            {"name": "Filip II", "start": 1556, "end": 1598},
            {"name": "Filip III", "start": 1598, "end": 1621},
            {"name": "Filip IV", "start": 1621, "end": 1665},
            {"name": "Karol II", "start": 1665, "end": 1700},
            {"name": "Filip V", "start": 1700, "end": 1746},
            {"name": "Ferdynand VI", "start": 1746, "end": 1759},
            {"name": "Karol III", "start": 1759, "end": 1788},
            {"name": "Karol IV", "start": 1788, "end": 1808}
        ]
    },
    "Brandenburgia": {
        "bonus": "lepsza stal", "steel": 1.5,
        "rulers": [
            {"name": "Fryderyk I", "start": 1415, "end": 1440},
            {"name": "Fryderyk II Żelazny Ząb", "start": 1440, "end": 1470},
            {"name": "Albrecht III Achilles", "start": 1470, "end": 1486},
            {"name": "Jan Cicero", "start": 1486, "end": 1499},
            {"name": "Joachim I Nestor", "start": 1499, "end": 1535},
            {"name": "Joachim II Hektor", "start": 1535, "end": 1571},
            {"name": "Jan Jerzy", "start": 1571, "end": 1598},
            {"name": "Joachim Fryderyk", "start": 1598, "end": 1608},
            {"name": "Jan Zygmunt", "start": 1608, "end": 1619},
            {"name": "Jerzy Wilhelm", "start": 1619, "end": 1640},
            {"name": "Fryderyk Wilhelm Wielki Elektor", "start": 1640, "end": 1688},
            {"name": "Fryderyk III", "start": 1688, "end": 1713},
            {"name": "Fryderyk Wilhelm I", "start": 1713, "end": 1740},
            {"name": "Fryderyk II Wielki", "start": 1740, "end": 1786},
            {"name": "Fryderyk Wilhelm II", "start": 1786, "end": 1797}
        ]
    }
}

# ============== BUDYNKI ==============
# === BUDYNKI ===
BUILDINGS = {

    # === MIESZKANIA ===
    "namiot": {
        "base_cost": {}, "build_time": 0, "base_workers": 0,
        "allowed_terrain": ["osada", "dzielnica"],
        "requires_settlement": True,
        "upgrades": [
            {"name": "Chata", "cost": {"drewno": 15}, "build_time": 3, "capacity": 6},
            {"name": "Dom", "cost": {"drewno": 30, "żelazo": 10}, "build_time": 7, "capacity": 8},
            {"name": "Dworek", "cost": {"drewno": 50, "żelazo": 20}, "build_time": 14, "capacity": 12}
        ]
    },

    # === DREWNO ===
    "drwalnia": {
        "base_cost": {"drewno": 20}, "build_time": 5, "base_workers": 2,
        "allowed_terrain": ["las"], "base_prod": {"drewno": 2},
        "upgrades": [
            {"name": "Tartak ręczny", "cost": {"drewno": 40, "żelazo": 10}, "build_time": 10, "prod": {"drewno": 1}, "workers": 3},
            {"name": "Tartak parowy", "cost": {"stal": 30, "żelazo": 20}, "build_time": 18, "prod": {"drewno": 2}, "workers": 4},
            {"name": "Przemysłowy kompleks drzewny", "cost": {"stal": 60, "cukier": 10}, "build_time": 30, "prod": {"drewno": 3}, "workers": 6}
        ]
    },

    # === ŻYWNOŚĆ ===
    "pole_uprawne": {
        "base_cost": {"drewno": 15}, "build_time": 4, "base_workers": 2,
        "allowed_terrain": ["pole"], "base_prod": {"żywność": 3},
        "upgrades": [
            {"name": "Gospodarstwo rolne", "cost": {"drewno": 30}, "build_time": 8, "prod": {"żywność": 1}, "workers": 3},
            {"name": "Plantacja zbożowa", "cost": {"żelazo": 20, "stal": 10}, "build_time": 15, "prod": {"żywność": 2}, "workers": 4},
            {"name": "Folwark z młynem", "cost": {"stal": 40, "cukier": 5}, "build_time": 25, "prod": {"żywność": 3}, "workers": 6}
        ]
    },

    # === SKÓRY → UBRANIA ===
    "obóz_myśliwski": {
        "base_cost": {"drewno": 25}, "build_time": 6, "base_workers": 2,
        "allowed_terrain": ["las", "pole"], "base_prod": {"skóry": 1.5},
        "upgrades": [
            {"name": "Stanica łowiecka", "cost": {"drewno": 40, "żelazo": 15}, "build_time": 10, "prod": {"skóry": 1}, "workers": 3},
            {"name": "Rezerwat skórny", "cost": {"stal": 30}, "build_time": 16, "prod": {"skóry": 1.5}, "workers": 4},
            {"name": "Kompania futrzarska", "cost": {"stal": 50, "cygara": 5}, "build_time": 25, "prod": {"skóry": 2}, "workers": 6}
        ]
    },
    "garbarnia_polowa": {
        "base_cost": {"drewno": 30, "żelazo": 10}, "build_time": 8, "base_workers": 2,
        "allowed_terrain": ["osada", "dzielnica"],
        "requires_settlement": True, "consumes": {"skóry": 1}, "base_prod": {"ubrania": 0.8},
        "upgrades": [
            {"name": "Warsztat krawiecki", "cost": {"drewno": 50, "stal": 15}, "build_time": 12, "prod": {"ubrania": 0.5}, "workers": 3},
            {"name": "Manufaktura odzieżowa", "cost": {"stal": 40, "cukier": 10}, "build_time": 20, "prod": {"ubrania": 1}, "workers": 4},
            {"name": "Fabryka tekstyliów kolonialnych", "cost": {"stal": 80, "cygara": 10}, "build_time": 30, "prod": {"ubrania": 1.5}, "workers": 6}
        ]
    },

    # === ZIOŁA → MEDYKAMENTY ===
    "ziołorośla": {
        "base_cost": {"drewno": 20}, "build_time": 5, "base_workers": 1,
        "allowed_terrain": ["pole", "las"], "base_prod": {"zioła": 1},
        "upgrades": [
            {"name": "Ogród botaniczny", "cost": {"drewno": 35, "żelazo": 10}, "build_time": 9, "prod": {"zioła": 0.8}, "workers": 2},
            {"name": "Plantacja ziół leczniczych", "cost": {"stal": 25}, "build_time": 14, "prod": {"zioła": 1.2}, "workers": 3},
            {"name": "Instytut Etnobotaniki", "cost": {"stal": 50, "medykamenty": 5}, "build_time": 22, "prod": {"zioła": 1.8}, "workers": 5}
        ]
    },
    "ziołolecznica": {
        "base_cost": {"drewno": 40, "żelazo": 15}, "build_time": 10, "base_workers": 2,
        "allowed_terrain": ["osada", "dzielnica"],
        "requires_settlement": True, "consumes": {"zioła": 1}, "base_prod": {"medykamenty": 0.6},
        "upgrades": [
            {"name": "Apteka kolonialna", "cost": {"stal": 30}, "build_time": 14, "prod": {"medykamenty": 0.4}, "workers": 3},
            {"name": "Laboratorium farmaceutyczne", "cost": {"stal": 50, "cukier": 10}, "build_time": 20, "prod": {"medykamenty": 0.8}, "workers": 4},
            {"name": "Instytut Medycyny Tropikalnej", "cost": {"stal": 100, "cygara": 15}, "build_time": 32, "prod": {"medykamenty": 1.2}, "workers": 6}
        ]
    },

    # === UNIWERSALNA KOPALNIA (węgiel, żelazo, srebro, złoto) ===
    "kopalnia": {
        "base_cost": {"drewno": 35, "żelazo": 15}, "build_time": 12, "base_workers": 3,
        "allowed_terrain": ["wzniesienia"],
        "base_prod": {},  # produkcja zależy od zasobu w komórce
        "upgrades": [
            {"name": "Szyb kopalniany", "cost": {"stal": 30}, "build_time": 16, "workers": 4},
            {"name": "Kopalnia głębinowa", "cost": {"stal": 60, "cukier": 5}, "build_time": 24, "workers": 5},
            {"name": "Kombinat górniczy", "cost": {"stal": 100, "cygara": 10}, "build_time": 35, "workers": 7}
        ]
    },

    # === STAL (przetwarzanie węgla + żelaza) ===
    "kuźnia_polowa": {
        "base_cost": {"drewno": 50, "żelazo": 20}, "build_time": 14, "base_workers": 3,
        "requires_settlement": True,
        "allowed_terrain": ["osada", "dzielnica"],
        "consumes": {"węgiel": 1, "żelazo": 1}, "base_prod": {"stal": 0.5},
        "upgrades": [
            {"name": "Huta surówki", "cost": {"stal": 40}, "build_time": 18, "prod": {"stal": 0.4}, "workers": 4},
            {"name": "Wielki piec martenowski", "cost": {"stal": 80, "cukier": 10}, "build_time": 25, "prod": {"stal": 0.8}, "workers": 5},
            {"name": "Huta stali Siemens-Martin", "cost": {"stal": 120, "cygara": 15}, "build_time": 38, "prod": {"stal": 1.2}, "workers": 7}
        ]
    },

    # === TRZCINA → CUKIER ===
    "plantacja_trzciny": {
        "base_cost": {"drewno": 30}, "build_time": 7, "base_workers": 3,
        "allowed_terrain": ["pole"], "base_prod": {"trzcina": 2},
        "upgrades": [
            {"name": "Hacienda trzcinowa", "cost": {"żelazo": 25}, "build_time": 12, "prod": {"trzcina": 1}, "workers": 4},
            {"name": "Latifundium cukrowe", "cost": {"stal": 40}, "build_time": 20, "prod": {"trzcina": 1.5}, "workers": 5},
            {"name": "Korporacja trzcinowa", "cost": {"stal": 80, "cygara": 10}, "build_time": 30, "prod": {"trzcina": 2}, "workers": 7}
        ]
    },
    "cukrownia_ręczna": {
        "base_cost": {"drewno": 45, "żelazo": 20}, "build_time": 12, "base_workers": 3,
        "allowed_terrain": ["osada", "dzielnica"],
        "requires_settlement": True, "consumes": {"trzcina": 2}, "base_prod": {"cukier": 1},
        "upgrades": [
            {"name": "Rafineria cukru", "cost": {"stal": 40}, "build_time": 16, "prod": {"cukier": 0.6}, "workers": 4},
            {"name": "Destylarnia cukru parowa", "cost": {"stal": 70, "cukier": 10}, "build_time": 24, "prod": {"cukier": 1}, "workers": 5},
            {"name": "Przemysłowa destylarnia cukru", "cost": {"stal": 110, "cygara": 15}, "build_time": 36, "prod": {"cukier": 1.5}, "workers": 7}
        ]
    },

    # === TYTOŃ → CYGARA ===
    "plantacja_tytoniu": {
        "base_cost": {"drewno": 35}, "build_time": 8, "base_workers": 3,
        "allowed_terrain": ["pole"], "base_prod": {"tytoń": 1.5},
        "upgrades": [
            {"name": "Estancia tytoniowa", "cost": {"żelazo": 30}, "build_time": 13, "prod": {"tytoń": 0.8}, "workers": 4},
            {"name": "Latifundium tytoniowe", "cost": {"stal": 50}, "build_time": 20, "prod": {"tytoń": 1.2}, "workers": 5},
            {"name": "Konsorcjum tytoniowe", "cost": {"stal": 90, "cygara": 10}, "build_time": 32, "prod": {"tytoń": 1.8}, "workers": 7}
        ]
    },
    "suszenie_tytoniu": {
        "base_cost": {"drewno": 50, "żelazo": 25}, "build_time": 14, "base_workers": 3,
        "requires_settlement": True, "consumes": {"tytoń": 1}, "base_prod": {"cygara": 0.7},
        "allowed_terrain": ["osada", "dzielnica"],
        "upgrades": [
            {"name": "Manufaktura cygar", "cost": {"stal": 45}, "build_time": 18, "prod": {"cygara": 0.5}, "workers": 4},
            {"name": "Fabryka cygar ręcznych", "cost": {"stal": 80, "cukier": 15}, "build_time": 26, "prod": {"cygara": 0.9}, "workers": 5},
            {"name": "Fabryka cygar premium", "cost": {"stal": 130, "cygara": 20}, "build_time": 40, "prod": {"cygara": 1.3}, "workers": 7}
        ]
    },

    # === PRZYSTAŃ ===
    "przystań": {
        "base_cost": {"drewno": 60, "żelazo": 30}, "build_time": 16, "base_workers": 0,
        "requires_adjacent_settlement": True,
        "allowed_terrain": ["morze"],
        "upgrades": []
    },

    # === DZIELNICA ===
    "dzielnica": {
        "base_cost": {"drewno": 120, "żelazo": 60, "stal": 20}, "build_time": 25, "base_workers": 5,
        "requires_adjacent_settlement": True,
        "allowed_terrain": ["las", "pole", "wzniesienia"],
        "upgrades": []
    }
}

# ============== INNE ==============
RESOURCES = ["żywność", "drewno", "skóry", "ubrania", "zioła", "medykamenty", "żelazo", "stal", "trzcina", "cukier", "tytoń", "cygara", "węgiel", "srebro", "złoto", "dukaty"]
MINE_RESOURCES = ["węgiel", "żelazo", "srebro", "złoto"]
MINE_COLORS = {"węgiel": "#000000", "żelazo": "#8B0000", "srebro": "#C0C0C0", "złoto": "#FFD700"}
MINE_NAMES = {"węgiel": "Węgiel", "żelazo": "Żelazo", "srebro": "Srebro", "złoto": "Złoto"}
BASE_COLORS = {"morze": "#0066CC", "pole": "#CCCC99", "las": "#228B22", "wzniesienia": "#8B4513", "osada": "#000000", "dzielnica": "#333333"}

# Misje królewskie
ROYAL_MISSIONS = [
    {"name": "Drewno na stocznie", "base": {"drewno": 200}},
    {"name": "Żywność dla armii", "base": {"żywność": 100, "skóry": 50}},
    {"name": "Żelazo na działa", "base": {"żelazo": 50}},
    {"name": "Stal dla floty", "base": {"stal": 60, "drewno": 100}},
    {"name": "Cukier dla dworu", "base": {"cukier": 100}},
    {"name": "Prezent dla króla", "base": {"złoto": 15, "cygara": 15, "srebro": 25}},
    {"name": "Złoto dla skarbu", "base": {"złoto": 20}},
    {"name": "Wsparcie dla armii", "base": {"stal": 30, "ubrania": 20}},
    {"name": "Zapomoga na choroby", "base": {"zioła": 15, "medykamenty": 20}},
    {"name": "Wsparcie kościoła", "base": {"złoto": 20, "srebro":30, "żywność": 20}},
]

EUROPE_PRICES = {
    "żywność": 1, "drewno": 8, "skóry": 4, "ubrania": 15,
    "zioła": 1, "medykamenty": 4, "trzcina": 3, "cukier": 12, "tytoń": 5, "cygara": 15,
    "żelazo": 10, "stal": 20, "złoto": 50, "srebro": 30, "węgiel": 3
}

NATIVE_PRICES = {
    "żywność": 8, "drewno": 2, "skóry": 3, "ubrania": 8,
    "zioła": 5, "medykamenty": 15,
    "żelazo": 5, "stal": 8, "złoto": 3, "srebro": 2, "węgiel": 1

}

TRIBES = ["Irokezi", "Czirokezi", "Apacze", "Siuksowie", "Krikowie", "Huronowie"]