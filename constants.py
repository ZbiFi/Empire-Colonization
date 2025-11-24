# constants.py
import random

# ============== DATY ==============
START_YEAR_MIN = 1492
START_YEAR_MAX = 1776

# Konfiguracja mapy
MAP_SIZE = 8

def generate_start_date():
    from datetime import datetime
    year = random.randint(START_YEAR_MIN, START_YEAR_MAX)
    month = random.randint(1, 12)
    day = random.randint(1, 28)
    return datetime(year, month, day)

# ile żywności zjada 1 osoba dziennie
FOOD_CONSUMPTION_PER_PERSON = 1.0

# mnożnik zużycia żywności dla osób ponad pojemność kolonii
FOOD_OVERCROWDING_MULTIPLIER = 1.5

# constants.py
MAX_SHIP_CARGO = 1500

# ============== PAŃSTWA ==============
STATES = {
'portugal': {'speed': 1.3,
              'rulers': [
                  {"name_key": "state.portugal.ruler.john_ii_the_perfect.name", "start": 1481, "end": 1495},
                  {"name_key": "state.portugal.ruler.manuel_i_the_fortunate.name", "start": 1495, "end": 1521},
                  {"name_key": "state.portugal.ruler.john_iii.name", "start": 1521, "end": 1557},
                  {"name_key": "state.portugal.ruler.sebastian_i.name", "start": 1557, "end": 1578},
                  {"name_key": "state.portugal.ruler.henry_i_the_cardinal.name", "start": 1578, "end": 1580},
                  {"name_key": "state.portugal.ruler.anthony_i.name", "start": 1580, "end": 1580},
                  {"name_key": "state.portugal.ruler.philip_i.name", "start": 1580, "end": 1598},
                  {"name_key": "state.portugal.ruler.philip_ii.name", "start": 1598, "end": 1621},
                  {"name_key": "state.portugal.ruler.philip_iii.name", "start": 1621, "end": 1640},
                  {"name_key": "state.portugal.ruler.john_iv_of_braganza.name", "start": 1640, "end": 1656},
                  {"name_key": "state.portugal.ruler.alfonso_vi.name", "start": 1656, "end": 1683},
                  {"name_key": "state.portugal.ruler.peter_ii.name", "start": 1683, "end": 1706},
                  {"name_key": "state.portugal.ruler.john_v.name", "start": 1706, "end": 1750},
                  {"name_key": "state.portugal.ruler.joseph_i_the_reformer.name", "start": 1750, "end": 1777},
                  {"name_key": "state.portugal.ruler.maria_i.name", "start": 1777, "end": 1816},
              ],
              'bonus_key': 'state.portugal.bonus',
              'name_key': 'state.portugal.name',
              'name': 'state.portugal.name'},
 'spain': {'explore': 1.4,
           'rulers': [
               {"name_key": "state.spain.ruler.isabella_i_of_castile.name", "start": 1474, "end": 1504},
               {"name_key": "state.spain.ruler.ferdinand_ii_of_aragon.name", "start": 1479, "end": 1516},
               {"name_key": "state.spain.ruler.joanna_the_mad.name", "start": 1504, "end": 1555},
               {"name_key": "state.spain.ruler.charles_i.name", "start": 1516, "end": 1556},
               {"name_key": "state.spain.ruler.philip_ii.name", "start": 1556, "end": 1598},
               {"name_key": "state.spain.ruler.philip_iii.name", "start": 1598, "end": 1621},
               {"name_key": "state.spain.ruler.philip_iv.name", "start": 1621, "end": 1665},
               {"name_key": "state.spain.ruler.charles_ii.name", "start": 1665, "end": 1700},
               {"name_key": "state.spain.ruler.philip_v_of_bourbon.name", "start": 1700, "end": 1746},
               {"name_key": "state.spain.ruler.ferdinand_vi.name", "start": 1746, "end": 1759},
               {"name_key": "state.spain.ruler.charles_iii.name", "start": 1759, "end": 1788},
               {"name_key": "state.spain.ruler.charles_iv.name", "start": 1788, "end": 1808},
           ],
           'bonus_key': 'state.spain.bonus',
           'name_key': 'state.spain.name',
           'name': 'state.spain.name'},
 'england': {'trade': 0.1,
             'speed': 1.1,
             'rulers': [
                 {"name_key": "state.england.ruler.henry_vii_tudor.name", "start": 1485, "end": 1509},
                 {"name_key": "state.england.ruler.henry_viii.name", "start": 1509, "end": 1547},
                 {"name_key": "state.england.ruler.edward_vi.name", "start": 1547, "end": 1553},
                 {"name_key": "state.england.ruler.mary_i_bloody.name", "start": 1553, "end": 1558},
                 {"name_key": "state.england.ruler.elizabeth_i.name", "start": 1558, "end": 1603},
                 {"name_key": "state.england.ruler.james_i_stuart.name", "start": 1603, "end": 1625},
                 {"name_key": "state.england.ruler.charles_i.name", "start": 1625, "end": 1649},
                 {"name_key": "state.england.ruler.commonwealth_of_england.name", "start": 1649, "end": 1653},
                 {"name_key": "state.england.ruler.oliver_cromwell_lord_protector.name", "start": 1653, "end": 1658},
                 {"name_key": "state.england.ruler.richard_cromwell.name", "start": 1658, "end": 1659},
                 {"name_key": "state.england.ruler.provisional_government_restoration.name", "start": 1659, "end": 1660},
                 {"name_key": "state.england.ruler.charles_ii.name", "start": 1660, "end": 1685},
                 {"name_key": "state.england.ruler.james_ii.name", "start": 1685, "end": 1688},
                 {"name_key": "state.england.ruler.william_iii_of_orange_and_mary_ii.name", "start": 1689, "end": 1702},
                 {"name_key": "state.england.ruler.anne_stuart.name", "start": 1702, "end": 1714},
                 {"name_key": "state.england.ruler.george_i_hanoverian.name", "start": 1714, "end": 1727},
                 {"name_key": "state.england.ruler.george_ii.name", "start": 1727, "end": 1760},
                 {"name_key": "state.england.ruler.george_iii.name", "start": 1760, "end": 1820},
             ],
             'bonus_key': 'state.england.bonus',
             'name_key': 'state.england.name',
             'name': 'state.england.name'},
 'france': {'reputation_threshold': 750,
            'rulers': [
                {"name_key": "state.france.ruler.charles_viii.name", "start": 1483, "end": 1498},
                {"name_key": "state.france.ruler.louis_xii.name", "start": 1498, "end": 1515},
                {"name_key": "state.france.ruler.francis_i.name", "start": 1515, "end": 1547},
                {"name_key": "state.france.ruler.henry_ii.name", "start": 1547, "end": 1559},
                {"name_key": "state.france.ruler.francis_ii.name", "start": 1559, "end": 1560},
                {"name_key": "state.france.ruler.charles_ix.name", "start": 1560, "end": 1574},
                {"name_key": "state.france.ruler.henry_iii.name", "start": 1574, "end": 1589},
                {"name_key": "state.france.ruler.henry_iv_of_bourbon.name", "start": 1589, "end": 1610},
                {"name_key": "state.france.ruler.louis_xiii.name", "start": 1610, "end": 1643},
                {"name_key": "state.france.ruler.louis_xiv_sun_king.name", "start": 1643, "end": 1715},
                {"name_key": "state.france.ruler.louis_xv.name", "start": 1715, "end": 1774},
                {"name_key": "state.france.ruler.louis_xvi.name", "start": 1774, "end": 1792},
            ],
            'bonus_key': 'state.france.bonus',
            'name_key': 'state.france.name',
            'name': 'state.france.name'},
 'netherlands': {'build_cost': 0.8,
                 'rulers': [
                     {"name_key": "state.netherlands.ruler.philip_ii.name", "start": 1555, "end": 1581},
                     {"name_key": "state.netherlands.ruler.council_of_state.name", "start": 1581, "end": 1588},
                     {"name_key": "state.netherlands.ruler.maurice_of_orange.name", "start": 1585, "end": 1625},
                     {"name_key": "state.netherlands.ruler.frederick_henry_of_orange.name", "start": 1625, "end": 1647},
                     {"name_key": "state.netherlands.ruler.william_ii_of_orange.name", "start": 1647, "end": 1650},
                     {"name_key": "state.netherlands.ruler.first_stadtholderless_period.name", "start": 1650, "end": 1672},
                     {"name_key": "state.netherlands.ruler.william_iii_of_orange.name", "start": 1672, "end": 1702},
                     {"name_key": "state.netherlands.ruler.second_stadtholderless_period.name", "start": 1702, "end": 1747},
                     {"name_key": "state.netherlands.ruler.william_iv_of_orange.name", "start": 1747, "end": 1751},
                     {"name_key": "state.netherlands.ruler.william_v_of_orange.name", "start": 1751, "end": 1795},
                 ],
                 'bonus_key': 'state.netherlands.bonus',
                 'name_key': 'state.netherlands.name',
                 'name': 'state.netherlands.name'},
 'sweden': {'wood': 1.5,
            'rulers': [
                {"name_key": "state.sweden.ruler.sten_sture_the_elder.name", "start": 1470, "end": 1497},
                {"name_key": "state.sweden.ruler.john_of_oldenburg.name", "start": 1497, "end": 1502},
                {"name_key": "state.sweden.ruler.sten_sture_the_younger.name", "start": 1512, "end": 1520},
                {"name_key": "state.sweden.ruler.christian_ii.name", "start": 1520, "end": 1521},
                {"name_key": "state.sweden.ruler.gustav_i_vasa.name", "start": 1523, "end": 1560},
                {"name_key": "state.sweden.ruler.erik_xiv.name", "start": 1560, "end": 1568},
                {"name_key": "state.sweden.ruler.john_iii.name", "start": 1568, "end": 1592},
                {"name_key": "state.sweden.ruler.sigismund_iii_vasa.name", "start": 1592, "end": 1599},
                {"name_key": "state.sweden.ruler.charles_ix.name", "start": 1599, "end": 1611},
                {"name_key": "state.sweden.ruler.gustavus_adolphus.name", "start": 1611, "end": 1632},
                {"name_key": "state.sweden.ruler.christina.name", "start": 1632, "end": 1654},
                {"name_key": "state.sweden.ruler.charles_x_gustav.name", "start": 1654, "end": 1660},
                {"name_key": "state.sweden.ruler.charles_xi.name", "start": 1660, "end": 1697},
                {"name_key": "state.sweden.ruler.charles_xii.name", "start": 1697, "end": 1718},
                {"name_key": "state.sweden.ruler.ulrika_eleanora.name", "start": 1718, "end": 1720},
                {"name_key": "state.sweden.ruler.frederick_i.name", "start": 1720, "end": 1751},
                {"name_key": "state.sweden.ruler.adolf_frederick.name", "start": 1751, "end": 1771},
                {"name_key": "state.sweden.ruler.gustav_iii.name", "start": 1771, "end": 1792},
                {"name_key": "state.sweden.ruler.gustav_iv_adolf.name", "start": 1792, "end": 1809},
            ],
            'bonus_key': 'state.sweden.bonus',
            'name_key': 'state.sweden.name',
            'name': 'state.sweden.name'},
 'denmark': {'food': 1.4,
             'rulers': [
                 {"name_key": "state.denmark.ruler.john_of_oldenburg.name", "start": 1481, "end": 1513},
                 {"name_key": "state.denmark.ruler.christian_ii.name", "start": 1513, "end": 1523},
                 {"name_key": "state.denmark.ruler.frederick_i.name", "start": 1523, "end": 1533},
                 {"name_key": "state.denmark.ruler.christian_iii.name", "start": 1534, "end": 1559},
                 {"name_key": "state.denmark.ruler.frederick_ii.name", "start": 1559, "end": 1588},
                 {"name_key": "state.denmark.ruler.christian_iv.name", "start": 1588, "end": 1648},
                 {"name_key": "state.denmark.ruler.frederick_iii.name", "start": 1648, "end": 1670},
                 {"name_key": "state.denmark.ruler.christian_v.name", "start": 1670, "end": 1699},
                 {"name_key": "state.denmark.ruler.frederick_iv.name", "start": 1699, "end": 1730},
                 {"name_key": "state.denmark.ruler.christian_vi.name", "start": 1730, "end": 1746},
                 {"name_key": "state.denmark.ruler.frederick_v.name", "start": 1746, "end": 1766},
                 {"name_key": "state.denmark.ruler.christian_vii.name", "start": 1766, "end": 1808},
             ],
             'bonus_key': 'state.denmark.bonus',
             'name_key': 'state.denmark.name',
             'name': 'state.denmark.name'},
 'venice': {'trade': 0.2,
            'rulers': [
                {"name_key": "state.venice.ruler.agostino_barbarigo.name", "start": 1486, "end": 1501},
                {"name_key": "state.venice.ruler.leonardo_loredan.name", "start": 1501, "end": 1521},
                {"name_key": "state.venice.ruler.antonio_grimani.name", "start": 1521, "end": 1523},
                {"name_key": "state.venice.ruler.andrea_gritti.name", "start": 1523, "end": 1538},
                {"name_key": "state.venice.ruler.pietro_lando.name", "start": 1538, "end": 1545},
                {"name_key": "state.venice.ruler.francesco_donato.name", "start": 1545, "end": 1553},
                {"name_key": "state.venice.ruler.marcantonio_trivisan.name", "start": 1553, "end": 1554},
                {"name_key": "state.venice.ruler.francesco_venier.name", "start": 1554, "end": 1556},
                {"name_key": "state.venice.ruler.lorenzo_priuli.name", "start": 1556, "end": 1559},
                {"name_key": "state.venice.ruler.girolamo_priuli.name", "start": 1559, "end": 1567},
                {"name_key": "state.venice.ruler.pietro_loredan.name", "start": 1567, "end": 1570},
                {"name_key": "state.venice.ruler.alvise_i_mocenigo.name", "start": 1570, "end": 1577},
                {"name_key": "state.venice.ruler.sebastiano_venier.name", "start": 1577, "end": 1578},
                {"name_key": "state.venice.ruler.nicolo_da_ponte.name", "start": 1578, "end": 1585},
                {"name_key": "state.venice.ruler.pasquale_cicogna.name", "start": 1585, "end": 1595},
                {"name_key": "state.venice.ruler.marino_grimani.name", "start": 1595, "end": 1605},
                {"name_key": "state.venice.ruler.leonardo_donato.name", "start": 1606, "end": 1612},
                {"name_key": "state.venice.ruler.marcantonio_memmo.name", "start": 1612, "end": 1615},
                {"name_key": "state.venice.ruler.giovanni_bembo.name", "start": 1615, "end": 1618},
                {"name_key": "state.venice.ruler.nicolo_donato.name", "start": 1618, "end": 1618},
                {"name_key": "state.venice.ruler.antonio_priuli.name", "start": 1618, "end": 1623},
                {"name_key": "state.venice.ruler.francesco_contarini.name", "start": 1623, "end": 1624},
                {"name_key": "state.venice.ruler.giovanni_i_cornaro.name", "start": 1625, "end": 1629},
                {"name_key": "state.venice.ruler.nicolo_contarini.name", "start": 1630, "end": 1631},
                {"name_key": "state.venice.ruler.francesco_erizzo.name", "start": 1631, "end": 1646},
                {"name_key": "state.venice.ruler.francesco_molin.name", "start": 1646, "end": 1655},
                {"name_key": "state.venice.ruler.carlo_contarini.name", "start": 1655, "end": 1656},
                {"name_key": "state.venice.ruler.francesco_cornaro.name", "start": 1656, "end": 1656},
                {"name_key": "state.venice.ruler.bertuccio_valier.name", "start": 1656, "end": 1658},
                {"name_key": "state.venice.ruler.giovanni_pesaro.name", "start": 1658, "end": 1659},
                {"name_key": "state.venice.ruler.domenico_ii_contarini.name", "start": 1659, "end": 1675},
                {"name_key": "state.venice.ruler.nicolo_sagredo.name", "start": 1675, "end": 1676},
                {"name_key": "state.venice.ruler.alvise_contarini.name", "start": 1676, "end": 1684},
                {"name_key": "state.venice.ruler.marcantonio_giustinian.name", "start": 1684, "end": 1688},
                {"name_key": "state.venice.ruler.francesco_morosini.name", "start": 1688, "end": 1694},
                {"name_key": "state.venice.ruler.sylvester_valier.name", "start": 1694, "end": 1700},
                {"name_key": "state.venice.ruler.alvise_ii_mocenigo.name", "start": 1700, "end": 1709},
                {"name_key": "state.venice.ruler.giovanni_ii_cornaro.name", "start": 1709, "end": 1722},
                {"name_key": "state.venice.ruler.alvise_iii_mocenigo.name", "start": 1722, "end": 1732},
                {"name_key": "state.venice.ruler.carlo_ruzzini.name", "start": 1732, "end": 1735},
                {"name_key": "state.venice.ruler.alvise_pisani.name", "start": 1735, "end": 1741},
                {"name_key": "state.venice.ruler.pietro_grimani.name", "start": 1741, "end": 1752},
                {"name_key": "state.venice.ruler.francesco_loredan.name", "start": 1752, "end": 1762},
                {"name_key": "state.venice.ruler.marco_foscarini.name", "start": 1762, "end": 1763},
                {"name_key": "state.venice.ruler.alvise_iv_mocenigo.name", "start": 1763, "end": 1779},
                {"name_key": "state.venice.ruler.paolo_renier.name", "start": 1779, "end": 1789},
                {"name_key": "state.venice.ruler.ludovico_manin.name", "start": 1789, "end": 1797},
            ],
            'bonus_key': 'state.venice.bonus',
            'name_key': 'state.venice.name',
            'name': 'state.venice.name'},
 'genoa': {'mine': 1.2,
           'rulers': [
               {"name_key": "state.genoa.ruler.battista_fregoso.name", "start": 1478, "end": 1483},
            {"name_key": "state.genoa.ruler.paolo_fregoso.name", "start": 1483, "end": 1488},
            {"name_key": "state.genoa.ruler.louis_xii_of_france.name", "start": 1499, "end": 1512},
            {"name_key": "state.genoa.ruler.ottaviano_fregoso.name", "start": 1513, "end": 1515},
            {"name_key": "state.genoa.ruler.anthony_adorno.name", "start": 1522, "end": 1527},
            {"name_key": "state.genoa.ruler.theodore_trivulzio.name", "start": 1528, "end": 1531},
            {"name_key": "state.genoa.ruler.andrea_doria_informal.name", "start": 1528, "end": 1560},
            {"name_key": "state.genoa.ruler.giovanni_battista_lascaris.name", "start": 1561, "end": 1573},
            {"name_key": "state.genoa.ruler.gianandrea_giustiniani.name", "start": 1573, "end": 1575},
            {"name_key": "state.genoa.ruler.ambrogio_di_negro.name", "start": 1581, "end": 1583},
            {"name_key": "state.genoa.ruler.giovanni_battista_cattaneo.name", "start": 1607, "end": 1609},
            {"name_key": "state.genoa.ruler.giulio_della_torre.name", "start": 1611, "end": 1613},
            {"name_key": "state.genoa.ruler.pietro_de_franchi.name", "start": 1621, "end": 1623},
            {"name_key": "state.genoa.ruler.federico_de_franchi.name", "start": 1623, "end": 1625},
            {"name_key": "state.genoa.ruler.giovanni_luca_chiavari.name", "start": 1627, "end": 1629},
            {"name_key": "state.genoa.ruler.andrea_spinola.name", "start": 1629, "end": 1631},
            {"name_key": "state.genoa.ruler.leonardo_della_torre.name", "start": 1631, "end": 1633},
            {"name_key": "state.genoa.ruler.giovanni_francesco_brignole.name", "start": 1635, "end": 1637},
            {"name_key": "state.genoa.ruler.agostino_pallavicini.name", "start": 1637, "end": 1639},
            {"name_key": "state.genoa.ruler.giovanni_battista_durazzo.name", "start": 1675, "end": 1677},
            {"name_key": "state.genoa.ruler.francesco_maria_imperiale.name", "start": 1715, "end": 1717},
            {"name_key": "state.genoa.ruler.giuseppe_maria_imperiale.name", "start": 1727, "end": 1729},
            {"name_key": "state.genoa.ruler.domenico_invrea.name", "start": 1761, "end": 1763},
            {"name_key": "state.genoa.ruler.rodolfo_emilio_brignole.name", "start": 1787, "end": 1789},
            {"name_key": "state.genoa.ruler.alviso_lomellini.name", "start": 1791, "end": 1793},
            {"name_key": "state.genoa.ruler.giacomo_maria_brignole.name", "start": 1795, "end": 1797}
           ],
           'bonus_key': 'state.genoa.bonus',
           'name_key': 'state.genoa.name',
           'name': 'state.genoa.name'},
 'poland': {'pop_start': 10,
            'rulers': [
                {"name_key": "state.poland.ruler.casimir_iv_jagiellon.name", "start": 1447, "end": 1492},
                {"name_key": "state.poland.ruler.john_i_albert.name", "start": 1492, "end": 1501},
                {"name_key": "state.poland.ruler.alexander_jagiellon.name", "start": 1501, "end": 1506},
                {"name_key": "state.poland.ruler.sigismund_i_the_old.name", "start": 1506, "end": 1548},
                {"name_key": "state.poland.ruler.sigismund_ii_augustus.name", "start": 1548, "end": 1572},
                {"name_key": "state.poland.ruler.henry_of_valois.name", "start": 1573, "end": 1574},
                {"name_key": "state.poland.ruler.stephen_bathory.name", "start": 1576, "end": 1586},
                {"name_key": "state.poland.ruler.sigismund_iii_vasa.name", "start": 1587, "end": 1632},
                {"name_key": "state.poland.ruler.wladyslaw_iv_vasa.name", "start": 1632, "end": 1648},
                {"name_key": "state.poland.ruler.john_ii_casimir_vasa.name", "start": 1648, "end": 1668},
                {"name_key": "state.poland.ruler.michal_korybut_wisniowiecki.name", "start": 1669, "end": 1673},
                {"name_key": "state.poland.ruler.john_iii_sobieski.name", "start": 1674, "end": 1696},
                {"name_key": "state.poland.ruler.augustus_ii_the_strong_1.name", "start": 1697, "end": 1706},
                {"name_key": "state.poland.ruler.stanislaw_leszczynski_1704.name", "start": 1704, "end": 1709},
                {"name_key": "state.poland.ruler.augustus_ii_the_strong_2.name", "start": 1709, "end": 1733},
                {"name_key": "state.poland.ruler.stanislaw_leszczynski_1733.name", "start": 1733, "end": 1736},
                {"name_key": "state.poland.ruler.augustus_iii_of_saxony.name", "start": 1733, "end": 1763},
                {"name_key": "state.poland.ruler.stanislaus_august_poniatowski.name", "start": 1764, "end": 1795}
            ],
            'bonus_key': 'state.poland.bonus',
            'name_key': 'state.poland.name',
            'name': 'state.poland.name'},
 'brandenburg': {'steel': 1.5,
                 'rulers': [
                     {"name_key": "state.brandenburg.ruler.frederick_i.name", "start": 1415, "end": 1440},
                     {"name_key": "state.brandenburg.ruler.frederick_ii_iron_tooth.name", "start": 1440, "end": 1470},
                     {"name_key": "state.brandenburg.ruler.albert_iii_achilles.name", "start": 1470, "end": 1486},
                     {"name_key": "state.brandenburg.ruler.john_cicero.name", "start": 1486, "end": 1499},
                     {"name_key": "state.brandenburg.ruler.joachim_i_nestor.name", "start": 1499, "end": 1535},
                     {"name_key": "state.brandenburg.ruler.joachim_ii_hector.name", "start": 1535, "end": 1571},
                     {"name_key": "state.brandenburg.ruler.john_george.name", "start": 1571, "end": 1598},
                     {"name_key": "state.brandenburg.ruler.joachim_frederick.name", "start": 1598, "end": 1608},
                     {"name_key": "state.brandenburg.ruler.john_sigismund.name", "start": 1608, "end": 1619},
                     {"name_key": "state.brandenburg.ruler.george_william.name", "start": 1619, "end": 1640},
                     {"name_key": "state.brandenburg.ruler.frederick_william_the_great_elector.name", "start": 1640, "end": 1688},
                     {"name_key": "state.brandenburg.ruler.frederick_iii.name", "start": 1688, "end": 1713},
                     {"name_key": "state.brandenburg.ruler.frederick_william_i.name", "start": 1713, "end": 1740},
                     {"name_key": "state.brandenburg.ruler.frederick_ii_the_great.name", "start": 1740, "end": 1786},
                     {"name_key": "state.brandenburg.ruler.frederick_william_ii.name", "start": 1786, "end": 1797},
                 ],
                 'bonus_key': 'state.brandenburg.bonus',
                 'name_key': 'state.brandenburg.name',
                 'name': 'state.brandenburg.name'}}

BUILDINGS = {
    "tent": {
        "base_cost": {"skins": 10, "iron": 5},
        "build_time": 1,
        "base_workers": 0,
        "capacity": 4,
        "allowed_terrain": ["settlement", "district"],
        "requires_settlement": True,
        "upgrades": [
            {
                "cost": {"wood": 40, "iron": 5},
                "build_time": 7,
                "capacity": 6,
                "name_key": "building.tent.upgrade.hut",
            },
            {
                "cost": {"wood": 80, "iron": 10, "steel": 5, "skins": 5},
                "build_time": 21,
                "capacity": 10,
                "name_key": "building.tent.upgrade.house",
            },
            {
                "cost": {"wood": 120, "iron": 15, "steel": 10, "clothes": 10},
                "build_time": 60,
                "capacity": 15,
                "name_key": "building.tent.upgrade.manor",
            },
        ],
        "name_key": "building.tent.name",
    },

    "lumber_camp": {
        "base_cost": {"wood": 20},
        "build_time": 5,
        "base_workers": 2,
        "allowed_terrain": ["forest"],
        "base_prod": {"wood": 2},
        "upgrades": [
            {
                "cost": {"wood": 40, "iron": 10},
                "build_time": 14,
                "prod": {"wood": 3},
                "workers": 3,
                "name_key": "building.lumber_camp.upgrade.hand_sawmill",
            },
            {
                "cost": {"steel": 30, "iron": 20},
                "build_time": 24,
                "prod": {"wood": 4},
                "workers": 4,
                "name_key": "building.lumber_camp.upgrade.steam_sawmill",
            },
            {
                "cost": {"steel": 60, "sugar": 10},
                "build_time": 40,
                "prod": {"wood": 5},
                "workers": 5,
                "name_key": "building.lumber_camp.upgrade.industrial_logging_complex",
            },
        ],
        "name_key": "building.lumber_camp.name",
    },

    "cropland": {
        "base_cost": {"wood": 15},
        "build_time": 4,
        "base_workers": 2,
        "allowed_terrain": ["field"],
        "base_prod": {"food": 1.5},
        "upgrades": [
            {
                "cost": {"wood": 30},
                "build_time": 15,
                "prod": {"food": 2},
                "workers": 3,
                "name_key": "building.cropland.upgrade.farm",
            },
            {
                "cost": {"iron": 20, "steel": 10},
                "build_time": 22,
                "prod": {"food": 2.5},
                "workers": 4,
                "name_key": "building.cropland.upgrade.grain_plantation",
            },
            {
                "cost": {"steel": 40, "sugar": 5},
                "build_time": 30,
                "prod": {"food": 3},
                "workers": 5,
                "name_key": "building.cropland.upgrade.folwark_with_mill",
            },
        ],
        "name_key": "building.cropland.name",
    },

    "hunting_camp": {
        "base_cost": {"wood": 25},
        "build_time": 6,
        "base_workers": 2,
        "allowed_terrain": ["forest", "field"],
        "base_prod": {"skins": 1, "food": 1},
        "upgrades": [
            {
                "cost": {"wood": 40, "iron": 15},
                "build_time": 10,
                "prod": {"skins": 1, "food": 1},
                "workers": 3,
                "name_key": "building.hunting_camp.upgrade.shepherd_outpost",
            },
            {
                "cost": {"steel": 30},
                "build_time": 24,
                "prod": {"skins": 1.5, "food": 1.5},
                "workers": 4,
                "name_key": "building.hunting_camp.upgrade.hide_reserve",
            },
            {
                "cost": {"steel": 50, "cigars": 5},
                "build_time": 35,
                "prod": {"skins": 2, "food": 1.5},
                "workers": 5,
                "name_key": "building.hunting_camp.upgrade.fur_company",
            },
        ],
        "name_key": "building.hunting_camp.name",
    },

    "tannery": {
        "base_cost": {"wood": 30, "iron": 10},
        "build_time": 8,
        "base_workers": 2,
        "allowed_terrain": ["settlement", "district"],
        "requires_settlement": True,
        "consumes": {"skins": 1},
        "base_prod": {"clothes": 0.5},
        "upgrades": [
            {
                "cost": {"wood": 50, "steel": 15},
                "build_time": 16,
                "prod": {"clothes": 0.6},
                "workers": 3,
                "name_key": "building.tannery.upgrade.tailor_workshop",
            },
            {
                "cost": {"steel": 40, "sugar": 10},
                "build_time": 27,
                "prod": {"clothes": 0.8},
                "workers": 4,
                "name_key": "building.tannery.upgrade.clothing_manufactory",
            },
            {
                "cost": {"steel": 80, "cigars": 10},
                "build_time": 45,
                "prod": {"clothes": 1},
                "workers": 5,
                "name_key": "building.tannery.upgrade.colonial_textile_factory",
            },
        ],
        "name_key": "building.tannery.name",
    },

    "herb_garden": {
        "base_cost": {"wood": 20},
        "build_time": 5,
        "base_workers": 2,
        "allowed_terrain": ["field", "forest"],
        "base_prod": {"herbs": 1},
        "upgrades": [
            {
                "cost": {"wood": 35, "iron": 10},
                "build_time": 13,
                "prod": {"herbs": 1.2},
                "workers": 3,
                "name_key": "building.herb_garden.upgrade.botanical_garden",
            },
            {
                "cost": {"steel": 25},
                "build_time": 20,
                "prod": {"herbs": 1.4},
                "workers": 4,
                "name_key": "building.herb_garden.upgrade.medicinal_herb_plantation",
            },
            {
                "cost": {"steel": 50, "meds": 5},
                "build_time": 43,
                "prod": {"herbs": 1.6},
                "workers": 5,
                "name_key": "building.herb_garden.upgrade.ethnobotany_institute",
            },
        ],
        "name_key": "building.herb_garden.name",
    },

    "herbal_clinic": {
        "base_cost": {"wood": 40, "iron": 15},
        "build_time": 10,
        "base_workers": 2,
        "allowed_terrain": ["settlement", "district"],
        "requires_settlement": True,
        "consumes": {"herbs": 1},
        "base_prod": {"meds": 0.5},
        "upgrades": [
            {
                "cost": {"steel": 30},
                "build_time": 14,
                "prod": {"meds": 0.6},
                "workers": 3,
                "name_key": "building.herbal_clinic.upgrade.colonial_pharmacy",
            },
            {
                "cost": {"steel": 50, "sugar": 10},
                "build_time": 20,
                "prod": {"meds": 0.8},
                "workers": 4,
                "name_key": "building.herbal_clinic.upgrade.pharmaceutical_laboratory",
            },
            {
                "cost": {"steel": 100, "cigars": 15},
                "build_time": 32,
                "prod": {"meds": 1},
                "workers": 5,
                "name_key": "building.herbal_clinic.upgrade.tropical_medicine_institute",
            },
        ],
        "name_key": "building.herbal_clinic.name",
    },

    "mine": {
        "base_cost": {"wood": 35, "iron": 15},
        "build_time": 12,
        "base_workers": 3,
        "base_prod": {"cane": 1},
        "allowed_terrain": ["hills"],
        "upgrades": [
            {
                "cost": {"steel": 30},
                "build_time": 16,
                "base_prod": {"cane": 1.2},
                "workers": 4,
                "name_key": "building.mine.upgrade.mining_shaft",
            },
            {
                "cost": {"steel": 60, "sugar": 5},
                "build_time": 24,
                "base_prod": {"cane": 1.4},
                "workers": 5,
                "name_key": "building.mine.upgrade.deep_mine",
            },
            {
                "cost": {"steel": 100, "cigars": 10},
                "build_time": 35,
                "base_prod": {"cane": 1.6},
                "workers": 7,
                "name_key": "building.mine.upgrade.mining_combine",
            },
        ],
        "name_key": "building.mine.name",
    },

    "field_forge": {
        "base_cost": {"wood": 50, "iron": 20},
        "build_time": 14,
        "base_workers": 3,
        "requires_settlement": True,
        "allowed_terrain": ["settlement", "district"],
        "consumes": {"coal": 1, "iron": 1},
        "base_prod": {"steel": 0.5},
        "upgrades": [
            {
                "cost": {"steel": 40},
                "build_time": 18,
                "prod": {"steel": 0.6},
                "workers": 4,
                "name_key": "building.field_forge.upgrade.pig_iron_smelter",
            },
            {
                "cost": {"steel": 80, "sugar": 10},
                "build_time": 25,
                "prod": {"steel": 0.8},
                "workers": 5,
                "name_key": "building.field_forge.upgrade.martin_furnace",
            },
            {
                "cost": {"steel": 120, "cigars": 15},
                "build_time": 38,
                "prod": {"steel": 1},
                "workers": 6,
                "name_key": "building.field_forge.upgrade.siemens_martin_steelworks",
            },
        ],
        "name_key": "building.field_forge.name",
    },

    "sugarcane_plantation": {
        "base_cost": {"wood": 30},
        "build_time": 7,
        "base_workers": 3,
        "allowed_terrain": ["field"],
        "base_prod": {"cane": 1},
        "upgrades": [
            {
                "cost": {"iron": 25},
                "build_time": 12,
                "prod": {"cane": 1.2},
                "workers": 4,
                "name_key": "building.sugarcane_plantation.upgrade.hacienda",
            },
            {
                "cost": {"steel": 40},
                "build_time": 20,
                "prod": {"cane": 1.4},
                "workers": 5,
                "name_key": "building.sugarcane_plantation.upgrade.sugar_latifundium",
            },
            {
                "cost": {"steel": 80, "cigars": 10},
                "build_time": 30,
                "prod": {"cane": 1.6},
                "workers": 6,
                "name_key": "building.sugarcane_plantation.upgrade.sugar_corporation",
            },
        ],
        "name_key": "building.sugarcane_plantation.name",
    },

    "manual_sugar_mill": {
        "base_cost": {"wood": 45, "iron": 20},
        "build_time": 12,
        "base_workers": 3,
        "allowed_terrain": ["settlement", "district"],
        "requires_settlement": True,
        "consumes": {"cane": 2},
        "base_prod": {"sugar": 0.5},
        "upgrades": [
            {
                "cost": {"steel": 40},
                "build_time": 16,
                "prod": {"sugar": 0.6},
                "workers": 4,
                "name_key": "building.manual_sugar_mill.upgrade.sugar_refinery",
            },
            {
                "cost": {"steel": 70, "sugar": 10},
                "build_time": 24,
                "prod": {"sugar": 0.7},
                "workers": 5,
                "name_key": "building.manual_sugar_mill.upgrade.steam_sugar_distillery",
            },
            {
                "cost": {"steel": 110, "cigars": 15},
                "build_time": 36,
                "prod": {"sugar": 0.8},
                "workers": 6,
                "name_key": "building.manual_sugar_mill.upgrade.industrial_sugar_distillery",
            },
        ],
        "name_key": "building.manual_sugar_mill.name",
    },

    "tobacco_plantation": {
        "base_cost": {"wood": 35},
        "build_time": 8,
        "base_workers": 3,
        "allowed_terrain": ["field"],
        "base_prod": {"tobacco": 1},
        "upgrades": [
            {
                "cost": {"iron": 30},
                "build_time": 13,
                "prod": {"tobacco": 1.2},
                "workers": 4,
                "name_key": "building.tobacco_plantation.upgrade.estancia",
            },
            {
                "cost": {"steel": 50},
                "build_time": 20,
                "prod": {"tobacco": 1.4},
                "workers": 5,
                "name_key": "building.tobacco_plantation.upgrade.tobacco_latifundium",
            },
            {
                "cost": {"steel": 90, "cigars": 10},
                "build_time": 32,
                "prod": {"tobacco": 1.6},
                "workers": 6,
                "name_key": "building.tobacco_plantation.upgrade.tobacco_consortium",
            },
        ],
        "name_key": "building.tobacco_plantation.name",
    },

    "tobacco_drying_house": {
        "base_cost": {"wood": 50, "iron": 25},
        "build_time": 14,
        "base_workers": 3,
        "requires_settlement": True,
        "consumes": {"tobacco": 1},
        "base_prod": {"cigars": 0.5},
        "allowed_terrain": ["settlement", "district"],
        "upgrades": [
            {
                "cost": {"steel": 45},
                "build_time": 18,
                "prod": {"cigars": 0.6},
                "workers": 4,
                "name_key": "building.tobacco_drying_house.upgrade.cigar_manufactory",
            },
            {
                "cost": {"steel": 80, "sugar": 15},
                "build_time": 26,
                "prod": {"cigars": 0.7},
                "workers": 5,
                "name_key": "building.tobacco_drying_house.upgrade.handmade_cigar_factory",
            },
            {
                "cost": {"steel": 130, "cigars": 20},
                "build_time": 40,
                "prod": {"cigars": 0.8},
                "workers": 6,
                "name_key": "building.tobacco_drying_house.upgrade.premium_cigar_factory",
            },
        ],
        "name_key": "building.tobacco_drying_house.name",
    },

    "harbor": {
        "base_cost": {"wood": 60, "iron": 30},
        "build_time": 16,
        "base_workers": 2,
        "base_prod": {"food": 2},
        "requires_adjacent_settlement": True,
        "allowed_terrain": ["sea"],
        "upgrades": [],
        "name_key": "building.harbor.name",
    },

    "district": {
        "base_cost": {"wood": 120, "iron": 60, "steel": 20},
        "build_time": 25,
        "base_workers": 5,
        "requires_adjacent_settlement": True,
        "allowed_terrain": ["forest", "field", "hills"],
        "upgrades": [],
        "name_key": "building.district.name",
    },
}

RESOURCES = [
    "food", "wood", "skins", "clothes", "herbs", "meds",
    "iron", "steel", "cane", "sugar", "tobacco", "cigars",
    "coal", "silver", "gold", "ducats"
]

MINE_RESOURCES = ["coal", "iron", "silver", "gold"]

MINE_COLORS = {
    "coal": "#000000",
    "iron": "#8B0000",
    "silver": "#C0C0C0",
    "gold": "#FFD700"
}

MINE_NAMES = {
    "coal": "mine.coal.name",
    "iron": "mine.iron.name",
    "silver": "mine.silver.name",
    "gold": "mine.gold.name"
}

BASE_COLORS = {
    "sea": "#0066CC",
    "field": "#CCCC99",
    "forest": "#228B22",
    "hills": "#8B4513",
    "settlement": "#000000",
    "district": "#333333"
}

# Misje królewskie
ROYAL_MISSIONS = [
    {
        "name_key": "mission.royal.shipyard_wood.name",
        "desc_key": "mission.royal.shipyard_wood.desc",
        "base": {"wood": 300},
    },
    {
        "name_key": "mission.royal.army_food.name",
        "desc_key": "mission.royal.army_food.desc",
        "base": {"food": 300, "skins": 50},
    },
    {
        "name_key": "mission.royal.cannons_iron.name",
        "desc_key": "mission.royal.cannons_iron.desc",
        "base": {"iron": 100},
    },
    {
        "name_key": "mission.royal.fleet_steel.name",
        "desc_key": "mission.royal.fleet_steel.desc",
        "base": {"steel": 60, "wood": 200},
    },
    {
        "name_key": "mission.royal.court_sugar.name",
        "desc_key": "mission.royal.court_sugar.desc",
        "base": {"sugar": 200},
    },
    {
        "name_key": "mission.royal.gift_for_king.name",
        "desc_key": "mission.royal.gift_for_king.desc",
        "base": {"gold": 50, "cigars": 30, "silver": 100},
    },
    {
        "name_key": "mission.royal.treasury_gold.name",
        "desc_key": "mission.royal.treasury_gold.desc",
        "base": {"gold": 100},
    },
    {
        "name_key": "mission.royal.army_support.name",
        "desc_key": "mission.royal.army_support.desc",
        "base": {"steel": 50, "clothes": 100},
    },
    {
        "name_key": "mission.royal.disease_relief.name",
        "desc_key": "mission.royal.disease_relief.desc",
        "base": {"herbs": 50, "meds": 70},
    },
    {
        "name_key": "mission.royal.church_support.name",
        "desc_key": "mission.royal.church_support.desc",
        "base": {"gold": 30, "silver": 50, "food": 100},
    },
]

NATIVE_MISSIONS_DETAILS = [
    {
        "name_key": "mission.native.bison_hunt_help.name",
        "desc_key": "mission.native.bison_hunt_help.desc",
        "base": {"food": 30, "iron": 20},
    },
    {
        "name_key": "mission.native.ancestors_hungry.name",
        "desc_key": "mission.native.ancestors_hungry.desc",
        "base": {"sugar": 20, "cigars": 20, "food": 30},
    },
    {
        "name_key": "mission.native.northerners_burn_villages.name",
        "desc_key": "mission.native.northerners_burn_villages.desc",
        "base": {"steel": 15, "iron": 30},
    },
    {
        "name_key": "mission.native.shaman_needs_herbs.name",
        "desc_key": "mission.native.shaman_needs_herbs.desc",
        "base": {"herbs": 30, "meds": 20},
    },
    {
        "name_key": "mission.native.women_want_fabrics.name",
        "desc_key": "mission.native.women_want_fabrics.desc",
        "base": {"clothes": 60},
    },
    {
        "name_key": "mission.native.stolen_chief_horse.name",
        "desc_key": "mission.native.stolen_chief_horse.desc",
        "base": {"iron": 20, "steel": 15},
    },
    {
        "name_key": "mission.native.great_spirit_shiny_stones.name",
        "desc_key": "mission.native.great_spirit_shiny_stones.desc",
        "base": {"gold": 10, "silver": 30},
    },
    {
        "name_key": "mission.native.sun_dance_feast.name",
        "desc_key": "mission.native.sun_dance_feast.desc",
        "base": {"sugar": 20, "food": 50},
    },
    {
        "name_key": "mission.native.children_sick.name",
        "desc_key": "mission.native.children_sick.desc",
        "base": {"meds": 15, "herbs": 30, "food": 40},
    },
    {
        "name_key": "mission.native.trade.name",
        "desc_key": "mission.native.trade.desc",
        "base": {"clothes": 30, "iron": 20, "cigars": 15},
    },
    {
        "name_key": "mission.native.prairie_drought.name",
        "desc_key": "mission.native.prairie_drought.desc",
        "base": {"food": 50, "herbs": 20},
    },
    {
        "name_key": "mission.native.warriors_return.name",
        "desc_key": "mission.native.warriors_return.desc",
        "base": {"food": 40, "cigars": 20},
    },
    {
        "name_key": "mission.native.palisade_repair.name",
        "desc_key": "mission.native.palisade_repair.desc",
        "base": {"wood": 60, "iron": 15},
    },
    {
        "name_key": "mission.native.new_tipis_for_winter.name",
        "desc_key": "mission.native.new_tipis_for_winter.desc",
        "base": {"skins": 40, "clothes": 20},
    },
    {
        "name_key": "mission.native.new_chief_naming_feast.name",
        "desc_key": "mission.native.new_chief_naming_feast.desc",
        "base": {"gold": 5, "silver": 15, "cigars": 10},
    },
    {
        "name_key": "mission.native.horses_need_shoes.name",
        "desc_key": "mission.native.horses_need_shoes.desc",
        "base": {"steel": 20, "iron": 20},
    },
    {
        "name_key": "mission.native.lost_hunters.name",
        "desc_key": "mission.native.lost_hunters.desc",
        "base": {"food": 30, "meds": 15},
    },
    {
        "name_key": "mission.native.silver_for_ancestors_graves.name",
        "desc_key": "mission.native.silver_for_ancestors_graves.desc",
        "base": {"silver": 30, "herbs": 10},
    },
    {
        "name_key": "mission.native.traders_cheated_elders.name",
        "desc_key": "mission.native.traders_cheated_elders.desc",
        "base": {"ducats": 40, "clothes": 25},
    },
    {
        "name_key": "mission.native.sacred_grove_fire.name",
        "desc_key": "mission.native.sacred_grove_fire.desc",
        "base": {"wood": 50, "food": 20, "cigars": 10},
    },
]

EUROPE_PRICES = {
    "food": 1, "wood": 8, "skins": 4, "clothes": 15,
    "herbs": 1, "meds": 4, "cane": 6, "sugar": 12, "tobacco": 8, "cigars": 15,
    "iron": 10, "steel": 20, "gold": 50, "silver": 30, "coal": 3
}

BLOCK_EUROPE_BUY = {"silver", "gold", "cane", "tobacco"}

NATIVE_PRICES = {
    "food": 8, "wood": 2, "skins": 3, "clothes": 8,
    "cane": 3, "sugar": 12, "tobacco": 5, "cigars": 15,
    "herbs": 5, "meds": 15,
    "iron": 5, "steel": 8, "gold": 3, "silver": 2, "coal": 1
}

BLOCK_NATIVE_BUY = {"meds", "clothes", "cigars", "sugar", "steel"}

TRIBES = ["Irokezi", "Czirokezi", "Apacze", "Siuksowie", "Krikowie", "Huronowie"]

# ============== PRODUKCJA INDIAN ==============
# min/max dziennej produkcji oraz min/max pojemności magazynu (na plemię)
NATIVE_RESOURCE_ECONOMY = {
    "food":   {"daily_prod": (5, 10),   "stockpile": (300, 500)},
    "skins":  {"daily_prod": (3, 5),    "stockpile": (150, 300)},
    "wood":   {"daily_prod": (5, 10),   "stockpile": (200, 400)},
    "herbs":  {"daily_prod": (3, 5),    "stockpile": (150, 300)},
    "cane":   {"daily_prod": (3, 5),    "stockpile": (100, 200)},
    "tobacco":{"daily_prod": (3, 5),    "stockpile": (50, 100)},
    "coal":   {"daily_prod": (1, 3),    "stockpile": (50, 100)},
    "iron":   {"daily_prod": (1, 3),    "stockpile": (50, 100)},
    "silver": {"daily_prod": (0.5, 2),  "stockpile": (30, 50)},
    "gold":   {"daily_prod": (0.5, 1),  "stockpile": (30, 50)},
}

# Mapping internal resource ids to localization keys
RESOURCE_DISPLAY_KEYS = {
    'sugar': 'res.sugar',
    'cigars': 'res.cigars',
    'wood': 'res.wood',
    'ducats': 'res.ducats',
    'meds': 'res.meds',
    'skins': 'res.skins',
    'silver': 'res.silver',
    'steel': 'res.steel',
    'cane': 'res.cane',
    'tobacco': 'res.tobacco',
    'clothes': 'res.clothes',
    'coal': 'res.coal',
    'herbs': 'res.herbs',
    'gold': 'res.gold',
    'iron': 'res.iron',
    'food': 'res.food'
}

# Mapping tribe internal names to localization keys
TRIBE_DISPLAY_KEYS = {
    'apaches': 'tribe.apache',
    'cherokees': 'tribe.cherokee',
    'hurons': 'tribe.huron',
    'iroquois': 'tribe.iroquois',
    'creeks': 'tribe.creek',
    'sioux': 'tribe.sioux'
}

SHIP_STATUS_IN_PORT = "in_port"
SHIP_STATUS_TO_EUROPE = "to_europe"
SHIP_STATUS_IN_EUROPE_PORT = "in_europe_port"
SHIP_STATUS_RETURNING = "returning"

SHIP_STATUS_KEYS = {
    SHIP_STATUS_IN_PORT: "ship.status.in_port",
    SHIP_STATUS_TO_EUROPE: "ship.status.to_europe",
    SHIP_STATUS_IN_EUROPE_PORT: "ship.status.in_europe_port",
    SHIP_STATUS_RETURNING: "ship.status.returning",
}