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
STATES = {'portugal': {'speed': 1.3,
              'rulers': [{'start': 1481, 'end': 1495, 'name_key': 'state.portugal.ruler.jan_ii_doskonay'},
                         {'start': 1495, 'end': 1521, 'name_key': 'state.portugal.ruler.manuel_i_szczesliwy'},
                         {'start': 1521, 'end': 1557, 'name_key': 'state.portugal.ruler.jan_iii'},
                         {'start': 1557, 'end': 1578, 'name_key': 'state.portugal.ruler.sebastian_i'},
                         {'start': 1578, 'end': 1580, 'name_key': 'state.portugal.ruler.henryk_i_kardyna'},
                         {'start': 1580, 'end': 1580, 'name_key': 'state.portugal.ruler.antoni_i'},
                         {'start': 1580, 'end': 1598, 'name_key': 'state.portugal.ruler.filip_i'},
                         {'start': 1598, 'end': 1621, 'name_key': 'state.portugal.ruler.filip_ii'},
                         {'start': 1621, 'end': 1640, 'name_key': 'state.portugal.ruler.filip_iii'},
                         {'start': 1640, 'end': 1656, 'name_key': 'state.portugal.ruler.jan_iv_braganca'},
                         {'start': 1656, 'end': 1683, 'name_key': 'state.portugal.ruler.alfons_vi'},
                         {'start': 1683, 'end': 1706, 'name_key': 'state.portugal.ruler.piotr_ii'},
                         {'start': 1706, 'end': 1750, 'name_key': 'state.portugal.ruler.jan_v'},
                         {'start': 1750, 'end': 1777, 'name_key': 'state.portugal.ruler.jozef_i_reformator'},
                         {'start': 1777, 'end': 1816, 'name_key': 'state.portugal.ruler.maria_i'}],
              'bonus_key': 'state.portugal.bonus',
              'name_key': 'state.portugal.name',
              'name': 'state.portugal.name'},
 'spain': {'explore': 1.4,
           'rulers': [{'start': 1474, 'end': 1504, 'name_key': 'state.spain.ruler.izabela_i_kastylijska'},
                      {'start': 1479, 'end': 1516, 'name_key': 'state.spain.ruler.ferdynand_ii_aragonski'},
                      {'start': 1504, 'end': 1555, 'name_key': 'state.spain.ruler.joanna_szalona'},
                      {'start': 1516, 'end': 1556, 'name_key': 'state.spain.ruler.karol_i'},
                      {'start': 1556, 'end': 1598, 'name_key': 'state.spain.ruler.filip_ii'},
                      {'start': 1598, 'end': 1621, 'name_key': 'state.spain.ruler.filip_iii'},
                      {'start': 1621, 'end': 1665, 'name_key': 'state.spain.ruler.filip_iv'},
                      {'start': 1665, 'end': 1700, 'name_key': 'state.spain.ruler.karol_ii'},
                      {'start': 1700, 'end': 1746, 'name_key': 'state.spain.ruler.filip_v_burbon'},
                      {'start': 1746, 'end': 1759, 'name_key': 'state.spain.ruler.ferdynand_vi'},
                      {'start': 1759, 'end': 1788, 'name_key': 'state.spain.ruler.karol_iii'},
                      {'start': 1788, 'end': 1808, 'name_key': 'state.spain.ruler.karol_iv'}],
           'bonus_key': 'state.spain.bonus',
           'name_key': 'state.spain.name',
           'name': 'state.spain.name'},
 'england': {'trade': 0.1,
             'speed': 1.1,
             'rulers': [{'start': 1485, 'end': 1509, 'name_key': 'state.england.ruler.henryk_vii_tudor'},
                        {'start': 1509, 'end': 1547, 'name_key': 'state.england.ruler.henryk_viii'},
                        {'start': 1547, 'end': 1553, 'name_key': 'state.england.ruler.edward_vi'},
                        {'start': 1553, 'end': 1558, 'name_key': 'state.england.ruler.maria_i_krwawa'},
                        {'start': 1558, 'end': 1603, 'name_key': 'state.england.ruler.elzbieta_i'},
                        {'start': 1603, 'end': 1625, 'name_key': 'state.england.ruler.jakub_i_stuart'},
                        {'start': 1625, 'end': 1649, 'name_key': 'state.england.ruler.karol_i'},
                        {'start': 1649, 'end': 1653, 'name_key': 'state.england.ruler.wspolnota_anglii_commonwealth'},
                        {'start': 1653, 'end': 1658, 'name_key': 'state.england.ruler.oliver_cromwell_lord_protektor'},
                        {'start': 1658, 'end': 1659, 'name_key': 'state.england.ruler.ryszard_cromwell'},
                        {'start': 1659, 'end': 1660, 'name_key': 'state.england.ruler.rzad_tymczasowy_restytucja'},
                        {'start': 1660, 'end': 1685, 'name_key': 'state.england.ruler.karol_ii'},
                        {'start': 1685, 'end': 1688, 'name_key': 'state.england.ruler.jakub_ii'},
                        {'start': 1689, 'end': 1702, 'name_key': 'state.england.ruler.wilhelm_iii_oranski_i_maria_ii'},
                        {'start': 1702, 'end': 1714, 'name_key': 'state.england.ruler.anna_stuart'},
                        {'start': 1714, 'end': 1727, 'name_key': 'state.england.ruler.jerzy_i_hanowerski'},
                        {'start': 1727, 'end': 1760, 'name_key': 'state.england.ruler.jerzy_ii'},
                        {'start': 1760, 'end': 1820, 'name_key': 'state.england.ruler.jerzy_iii'}],
             'bonus_key': 'state.england.bonus',
             'name_key': 'state.england.name',
             'name': 'state.england.name'},
 'france': {'reputation_threshold': 750,
            'rulers': [{'start': 1483, 'end': 1498, 'name_key': 'state.france.ruler.karol_viii'},
                       {'start': 1498, 'end': 1515, 'name_key': 'state.france.ruler.ludwik_xii'},
                       {'start': 1515, 'end': 1547, 'name_key': 'state.france.ruler.franciszek_i'},
                       {'start': 1547, 'end': 1559, 'name_key': 'state.france.ruler.henryk_ii'},
                       {'start': 1559, 'end': 1560, 'name_key': 'state.france.ruler.franciszek_ii'},
                       {'start': 1560, 'end': 1574, 'name_key': 'state.france.ruler.karol_ix'},
                       {'start': 1574, 'end': 1589, 'name_key': 'state.france.ruler.henryk_iii'},
                       {'start': 1589, 'end': 1610, 'name_key': 'state.france.ruler.henryk_iv_burbon'},
                       {'start': 1610, 'end': 1643, 'name_key': 'state.france.ruler.ludwik_xiii'},
                       {'start': 1643, 'end': 1715, 'name_key': 'state.france.ruler.ludwik_xiv_krol_sonce'},
                       {'start': 1715, 'end': 1774, 'name_key': 'state.france.ruler.ludwik_xv'},
                       {'start': 1774, 'end': 1792, 'name_key': 'state.france.ruler.ludwik_xvi'}],
            'bonus_key': 'state.france.bonus',
            'name_key': 'state.france.name',
            'name': 'state.france.name'},
 'netherlands': {'build_cost': 0.8,
                 'rulers': [{'start': 1555, 'end': 1581, 'name_key': 'state.netherlands.ruler.filip_ii'},
                            {'start': 1581, 'end': 1588, 'name_key': 'state.netherlands.ruler.rada_stanu'},
                            {'start': 1585, 'end': 1625, 'name_key': 'state.netherlands.ruler.maurycy_oranski'},
                            {'start': 1625, 'end': 1647, 'name_key': 'state.netherlands.ruler.fryderyk_henryk_oranski'},
                            {'start': 1647, 'end': 1650, 'name_key': 'state.netherlands.ruler.wilhelm_ii_oranski'},
                            {'start': 1650, 'end': 1672, 'name_key': 'state.netherlands.ruler.okres_bez_stadhoudera_i'},
                            {'start': 1672, 'end': 1702, 'name_key': 'state.netherlands.ruler.wilhelm_iii_oranski'},
                            {'start': 1702,
                             'end': 1747,
                             'name_key': 'state.netherlands.ruler.okres_bez_stadhoudera_ii'},
                            {'start': 1747, 'end': 1751, 'name_key': 'state.netherlands.ruler.wilhelm_iv_oranski'},
                            {'start': 1751, 'end': 1795, 'name_key': 'state.netherlands.ruler.wilhelm_v_oranski'}],
                 'bonus_key': 'state.netherlands.bonus',
                 'name_key': 'state.netherlands.name',
                 'name': 'state.netherlands.name'},
 'sweden': {'wood': 1.5,
            'rulers': [{'start': 1470, 'end': 1497, 'name_key': 'state.sweden.ruler.sten_starszy'},
                       {'start': 1497, 'end': 1501, 'name_key': 'state.sweden.ruler.jan_oldenburnski'},
                       {'start': 1501,
                        'end': 1503,
                        'name_key': 'state.sweden.ruler.sten_sture_starszy_regent_ii_okres'},
                       {'start': 1503, 'end': 1512, 'name_key': 'state.sweden.ruler.svante_nilsson_sture_regent'},
                       {'start': 1512, 'end': 1520, 'name_key': 'state.sweden.ruler.sten_sture_modszy'},
                       {'start': 1520, 'end': 1521, 'name_key': 'state.sweden.ruler.krystian_ii'},
                       {'start': 1521, 'end': 1523, 'name_key': 'state.sweden.ruler.gustaw_waza_regent'},
                       {'start': 1523, 'end': 1560, 'name_key': 'state.sweden.ruler.gustaw_i_waza'},
                       {'start': 1560, 'end': 1568, 'name_key': 'state.sweden.ruler.erik_xiv'},
                       {'start': 1568, 'end': 1592, 'name_key': 'state.sweden.ruler.jan_iii'},
                       {'start': 1592, 'end': 1599, 'name_key': 'state.sweden.ruler.zygmunt_iii_waza'},
                       {'start': 1599, 'end': 1611, 'name_key': 'state.sweden.ruler.karol_ix'},
                       {'start': 1611, 'end': 1632, 'name_key': 'state.sweden.ruler.gustaw_ii_adolf'},
                       {'start': 1632, 'end': 1654, 'name_key': 'state.sweden.ruler.krystyna'},
                       {'start': 1654, 'end': 1660, 'name_key': 'state.sweden.ruler.karol_x_gustaw'},
                       {'start': 1660, 'end': 1697, 'name_key': 'state.sweden.ruler.karol_xi'},
                       {'start': 1697, 'end': 1718, 'name_key': 'state.sweden.ruler.karol_xii'},
                       {'start': 1718, 'end': 1720, 'name_key': 'state.sweden.ruler.ulryka_eleonora'},
                       {'start': 1720, 'end': 1751, 'name_key': 'state.sweden.ruler.fryderyk_i'},
                       {'start': 1751, 'end': 1771, 'name_key': 'state.sweden.ruler.adolf_fryderyk'},
                       {'start': 1771, 'end': 1792, 'name_key': 'state.sweden.ruler.gustaw_iii'},
                       {'start': 1792, 'end': 1809, 'name_key': 'state.sweden.ruler.gustaw_iv_adolf'}],
            'bonus_key': 'state.sweden.bonus',
            'name_key': 'state.sweden.name',
            'name': 'state.sweden.name'},
 'denmark': {'food': 1.4,
             'rulers': [{'start': 1481, 'end': 1513, 'name_key': 'state.denmark.ruler.jan_oldenburnski'},
                        {'start': 1513, 'end': 1523, 'name_key': 'state.denmark.ruler.krystian_ii'},
                        {'start': 1523, 'end': 1533, 'name_key': 'state.denmark.ruler.fryderyk_i'},
                        {'start': 1533, 'end': 1534, 'name_key': 'state.denmark.ruler.interregnum'},
                        {'start': 1534, 'end': 1559, 'name_key': 'state.denmark.ruler.krystian_iii'},
                        {'start': 1559, 'end': 1588, 'name_key': 'state.denmark.ruler.fryderyk_ii'},
                        {'start': 1588, 'end': 1648, 'name_key': 'state.denmark.ruler.krystian_iv'},
                        {'start': 1648, 'end': 1670, 'name_key': 'state.denmark.ruler.fryderyk_iii'},
                        {'start': 1670, 'end': 1699, 'name_key': 'state.denmark.ruler.krystian_v'},
                        {'start': 1699, 'end': 1730, 'name_key': 'state.denmark.ruler.fryderyk_iv'},
                        {'start': 1730, 'end': 1746, 'name_key': 'state.denmark.ruler.krystian_vi'},
                        {'start': 1746, 'end': 1766, 'name_key': 'state.denmark.ruler.fryderyk_v'},
                        {'start': 1766, 'end': 1808, 'name_key': 'state.denmark.ruler.krystian_vii'}],
             'bonus_key': 'state.denmark.bonus',
             'name_key': 'state.denmark.name',
             'name': 'state.denmark.name'},
 'venice': {'trade': 0.2,
            'rulers': [{'start': 1486, 'end': 1501, 'name_key': 'state.venice.ruler.agostino_barbarigo'},
                       {'start': 1501, 'end': 1521, 'name_key': 'state.venice.ruler.leonardo_loredan'},
                       {'start': 1521, 'end': 1523, 'name_key': 'state.venice.ruler.antonio_grimani'},
                       {'start': 1523, 'end': 1538, 'name_key': 'state.venice.ruler.andrea_gritti'},
                       {'start': 1538, 'end': 1545, 'name_key': 'state.venice.ruler.pietro_lando'},
                       {'start': 1545, 'end': 1553, 'name_key': 'state.venice.ruler.francesco_donato'},
                       {'start': 1553, 'end': 1554, 'name_key': 'state.venice.ruler.marcantonio_trivisan'},
                       {'start': 1554, 'end': 1556, 'name_key': 'state.venice.ruler.francesco_venier'},
                       {'start': 1556, 'end': 1559, 'name_key': 'state.venice.ruler.lorenzo_priuli'},
                       {'start': 1559, 'end': 1567, 'name_key': 'state.venice.ruler.girolamo_priuli'},
                       {'start': 1567, 'end': 1570, 'name_key': 'state.venice.ruler.pietro_loredan'},
                       {'start': 1570, 'end': 1577, 'name_key': 'state.venice.ruler.alvise_i_mocenigo'},
                       {'start': 1577, 'end': 1578, 'name_key': 'state.venice.ruler.sebastiano_venier'},
                       {'start': 1578, 'end': 1585, 'name_key': 'state.venice.ruler.nicolo_da_ponte'},
                       {'start': 1585, 'end': 1595, 'name_key': 'state.venice.ruler.pasquale_cicogna'},
                       {'start': 1595, 'end': 1605, 'name_key': 'state.venice.ruler.marino_grimani'},
                       {'start': 1606, 'end': 1612, 'name_key': 'state.venice.ruler.leonardo_donato'},
                       {'start': 1612, 'end': 1615, 'name_key': 'state.venice.ruler.marcantonio_memmo'},
                       {'start': 1615, 'end': 1618, 'name_key': 'state.venice.ruler.giovanni_bembo'},
                       {'start': 1618, 'end': 1618, 'name_key': 'state.venice.ruler.nicolo_donato'},
                       {'start': 1618, 'end': 1623, 'name_key': 'state.venice.ruler.antonio_priuli'},
                       {'start': 1623, 'end': 1624, 'name_key': 'state.venice.ruler.francesco_contarini'},
                       {'start': 1625, 'end': 1629, 'name_key': 'state.venice.ruler.giovanni_i_cornaro'},
                       {'start': 1630, 'end': 1631, 'name_key': 'state.venice.ruler.nicolo_contarini'},
                       {'start': 1631, 'end': 1646, 'name_key': 'state.venice.ruler.francesco_erizzo'},
                       {'start': 1646, 'end': 1655, 'name_key': 'state.venice.ruler.francesco_molin'},
                       {'start': 1655, 'end': 1656, 'name_key': 'state.venice.ruler.carlo_contarini'},
                       {'start': 1656, 'end': 1656, 'name_key': 'state.venice.ruler.francesco_cornaro'},
                       {'start': 1656, 'end': 1658, 'name_key': 'state.venice.ruler.bertuccio_valier'},
                       {'start': 1658, 'end': 1659, 'name_key': 'state.venice.ruler.giovanni_pesaro'},
                       {'start': 1659, 'end': 1675, 'name_key': 'state.venice.ruler.domenico_ii_contarini'},
                       {'start': 1675, 'end': 1676, 'name_key': 'state.venice.ruler.nicolo_sagredo'},
                       {'start': 1676, 'end': 1684, 'name_key': 'state.venice.ruler.alvise_contarini'},
                       {'start': 1684, 'end': 1688, 'name_key': 'state.venice.ruler.marcantonio_giustinian'},
                       {'start': 1688, 'end': 1694, 'name_key': 'state.venice.ruler.francesco_morosini'},
                       {'start': 1694, 'end': 1700, 'name_key': 'state.venice.ruler.sylwester_valier'},
                       {'start': 1700, 'end': 1709, 'name_key': 'state.venice.ruler.alvise_ii_mocenigo'},
                       {'start': 1709, 'end': 1722, 'name_key': 'state.venice.ruler.giovanni_ii_cornaro'},
                       {'start': 1722, 'end': 1732, 'name_key': 'state.venice.ruler.alvise_iii_mocenigo'},
                       {'start': 1732, 'end': 1735, 'name_key': 'state.venice.ruler.carlo_ruzzini'},
                       {'start': 1735, 'end': 1741, 'name_key': 'state.venice.ruler.alvise_pisani'},
                       {'start': 1741, 'end': 1752, 'name_key': 'state.venice.ruler.pietro_grimani'},
                       {'start': 1752, 'end': 1762, 'name_key': 'state.venice.ruler.francesco_loredan'},
                       {'start': 1762, 'end': 1763, 'name_key': 'state.venice.ruler.marco_foscarini'},
                       {'start': 1763, 'end': 1779, 'name_key': 'state.venice.ruler.alvise_iv_mocenigo'},
                       {'start': 1779, 'end': 1789, 'name_key': 'state.venice.ruler.paolo_renier'},
                       {'start': 1789, 'end': 1797, 'name_key': 'state.venice.ruler.ludovico_manin'}],
            'bonus_key': 'state.venice.bonus',
            'name_key': 'state.venice.name',
            'name': 'state.venice.name'},
 'genoa': {'mine': 1.2,
           'rulers': [{'start': 1478, 'end': 1483, 'name_key': 'state.genoa.ruler.battista_fregoso'},
                      {'start': 1483, 'end': 1488, 'name_key': 'state.genoa.ruler.paolo_fregoso'},
                      {'start': 1499, 'end': 1512, 'name_key': 'state.genoa.ruler.ludwik_xii_francji'},
                      {'start': 1513, 'end': 1515, 'name_key': 'state.genoa.ruler.ottaviano_fregoso'},
                      {'start': 1522, 'end': 1527, 'name_key': 'state.genoa.ruler.antoni_adorno'},
                      {'start': 1528, 'end': 1531, 'name_key': 'state.genoa.ruler.teodoro_trivulzio'},
                      {'start': 1528, 'end': 1560, 'name_key': 'state.genoa.ruler.andrea_doria_nieformalny'},
                      {'start': 1561, 'end': 1573, 'name_key': 'state.genoa.ruler.giovanni_battista_lascaris'},
                      {'start': 1573, 'end': 1575, 'name_key': 'state.genoa.ruler.gianandrea_giustiniani'},
                      {'start': 1581, 'end': 1583, 'name_key': 'state.genoa.ruler.ambrogio_di_negro'},
                      {'start': 1583, 'end': 1607, 'name_key': 'state.genoa.ruler.republika_genui_kolejni_dozowie'},
                      {'start': 1607, 'end': 1609, 'name_key': 'state.genoa.ruler.giovanni_battista_cattaneo'},
                      {'start': 1609, 'end': 1611, 'name_key': 'state.genoa.ruler.republika_genui_kolejni_dozowie'},
                      {'start': 1611, 'end': 1613, 'name_key': 'state.genoa.ruler.giulio_della_torre'},
                      {'start': 1613, 'end': 1621, 'name_key': 'state.genoa.ruler.republika_genui_kolejni_dozowie'},
                      {'start': 1621, 'end': 1623, 'name_key': 'state.genoa.ruler.pietro_de_franchi'},
                      {'start': 1623, 'end': 1625, 'name_key': 'state.genoa.ruler.federico_de_franchi'},
                      {'start': 1627, 'end': 1629, 'name_key': 'state.genoa.ruler.giovanni_luca_chiavari'},
                      {'start': 1629, 'end': 1631, 'name_key': 'state.genoa.ruler.andrea_spinola'},
                      {'start': 1631, 'end': 1633, 'name_key': 'state.genoa.ruler.leonardo_della_torre'},
                      {'start': 1635, 'end': 1637, 'name_key': 'state.genoa.ruler.giovanni_francesco_brignole'},
                      {'start': 1637, 'end': 1639, 'name_key': 'state.genoa.ruler.agostino_pallavicini'},
                      {'start': 1639, 'end': 1675, 'name_key': 'state.genoa.ruler.republika_genui_kolejni_dozowie'},
                      {'start': 1675, 'end': 1677, 'name_key': 'state.genoa.ruler.giovanni_battista_durazzo'},
                      {'start': 1677, 'end': 1715, 'name_key': 'state.genoa.ruler.republika_genui_kolejni_dozowie'},
                      {'start': 1715, 'end': 1717, 'name_key': 'state.genoa.ruler.francesco_maria_imperiale'},
                      {'start': 1717, 'end': 1727, 'name_key': 'state.genoa.ruler.republika_genui_kolejni_dozowie'},
                      {'start': 1727, 'end': 1729, 'name_key': 'state.genoa.ruler.giuseppe_maria_imperiale'},
                      {'start': 1729, 'end': 1761, 'name_key': 'state.genoa.ruler.republika_genui_kolejni_dozowie'},
                      {'start': 1761, 'end': 1763, 'name_key': 'state.genoa.ruler.domenico_invrea'},
                      {'start': 1763, 'end': 1787, 'name_key': 'state.genoa.ruler.republika_genui_kolejni_dozowie'},
                      {'start': 1787, 'end': 1789, 'name_key': 'state.genoa.ruler.rodolfo_emilio_brignole'},
                      {'start': 1789, 'end': 1791, 'name_key': 'state.genoa.ruler.republika_genui_kolejni_dozowie'},
                      {'start': 1791, 'end': 1795, 'name_key': 'state.genoa.ruler.alviso_lomellini'},
                      {'start': 1795, 'end': 1797, 'name_key': 'state.genoa.ruler.giacomo_maria_brignole'}],
           'bonus_key': 'state.genoa.bonus',
           'name_key': 'state.genoa.name',
           'name': 'state.genoa.name'},
 'poland': {'pop_start': 10,
            'rulers': [{'start': 1447, 'end': 1492, 'name_key': 'state.poland.ruler.kazimierz_iv_jagiellonczyk'},
                       {'start': 1492, 'end': 1501, 'name_key': 'state.poland.ruler.jan_i_olbracht'},
                       {'start': 1501, 'end': 1506, 'name_key': 'state.poland.ruler.aleksander_jagiellonczyk'},
                       {'start': 1506, 'end': 1548, 'name_key': 'state.poland.ruler.zygmunt_i_stary'},
                       {'start': 1548, 'end': 1572, 'name_key': 'state.poland.ruler.zygmunt_ii_august'},
                       {'start': 1573, 'end': 1574, 'name_key': 'state.poland.ruler.henryk_walezy'},
                       {'start': 1576, 'end': 1586, 'name_key': 'state.poland.ruler.stefan_batory'},
                       {'start': 1587, 'end': 1632, 'name_key': 'state.poland.ruler.zygmunt_iii_waza'},
                       {'start': 1632, 'end': 1648, 'name_key': 'state.poland.ruler.wadysaw_iv_waza'},
                       {'start': 1648, 'end': 1668, 'name_key': 'state.poland.ruler.jan_ii_kazimierz_waza'},
                       {'start': 1669, 'end': 1673, 'name_key': 'state.poland.ruler.micha_korybut_wisniowiecki'},
                       {'start': 1674, 'end': 1696, 'name_key': 'state.poland.ruler.jan_iii_sobieski'},
                       {'start': 1697, 'end': 1706, 'name_key': 'state.poland.ruler.august_ii_mocny'},
                       {'start': 1704, 'end': 1709, 'name_key': 'state.poland.ruler.stanisaw_leszczynski'},
                       {'start': 1709, 'end': 1733, 'name_key': 'state.poland.ruler.august_ii_mocny'},
                       {'start': 1733, 'end': 1736, 'name_key': 'state.poland.ruler.stanisaw_leszczynski'},
                       {'start': 1733, 'end': 1763, 'name_key': 'state.poland.ruler.august_iii_sas'},
                       {'start': 1764, 'end': 1795, 'name_key': 'state.poland.ruler.stanisaw_august_poniatowski'}],
            'bonus_key': 'state.poland.bonus',
            'name_key': 'state.poland.name',
            'name': 'state.poland.name'},
 'brandenburg': {'steel': 1.5,
                 'rulers': [{'start': 1415, 'end': 1440, 'name_key': 'state.brandenburg.ruler.fryderyk_i'},
                            {'start': 1440, 'end': 1470, 'name_key': 'state.brandenburg.ruler.fryderyk_ii_zelazny_zab'},
                            {'start': 1470, 'end': 1486, 'name_key': 'state.brandenburg.ruler.albrecht_iii_achilles'},
                            {'start': 1486, 'end': 1499, 'name_key': 'state.brandenburg.ruler.jan_cicero'},
                            {'start': 1499, 'end': 1535, 'name_key': 'state.brandenburg.ruler.joachim_i_nestor'},
                            {'start': 1535, 'end': 1571, 'name_key': 'state.brandenburg.ruler.joachim_ii_hektor'},
                            {'start': 1571, 'end': 1598, 'name_key': 'state.brandenburg.ruler.jan_jerzy'},
                            {'start': 1598, 'end': 1608, 'name_key': 'state.brandenburg.ruler.joachim_fryderyk'},
                            {'start': 1608, 'end': 1619, 'name_key': 'state.brandenburg.ruler.jan_zygmunt'},
                            {'start': 1619, 'end': 1640, 'name_key': 'state.brandenburg.ruler.jerzy_wilhelm'},
                            {'start': 1640,
                             'end': 1688,
                             'name_key': 'state.brandenburg.ruler.fryderyk_wilhelm_wielki_elektor'},
                            {'start': 1688, 'end': 1713, 'name_key': 'state.brandenburg.ruler.fryderyk_iii'},
                            {'start': 1713, 'end': 1740, 'name_key': 'state.brandenburg.ruler.fryderyk_wilhelm_i'},
                            {'start': 1740, 'end': 1786, 'name_key': 'state.brandenburg.ruler.fryderyk_ii_wielki'},
                            {'start': 1786, 'end': 1797, 'name_key': 'state.brandenburg.ruler.fryderyk_wilhelm_ii'}],
                 'bonus_key': 'state.brandenburg.bonus',
                 'name_key': 'state.brandenburg.name',
                 'name': 'state.brandenburg.name'}}

BUILDINGS = {
    'tent': {
        'base_cost': {'skóry': 10, 'żelazo': 5},
        'build_time': 1,
        'base_workers': 0,
        'capacity': 4,
        'allowed_terrain': ['osada', 'dzielnica'],
        'requires_settlement': True,
        'upgrades': [
            {
                'cost': {'drewno': 40, 'żelazo': 5},
                'build_time': 7,
                'capacity': 6,
                'name_key': 'building.tent.upgrade.hut'
            },
            {
                'cost': {'drewno': 80, 'żelazo': 10, 'stal': 5, 'skóry': 5},
                'build_time': 21,
                'capacity': 10,
                'name_key': 'building.tent.upgrade.house'
            },
            {
                'cost': {'drewno': 120, 'żelazo': 15, 'stal': 10, 'ubrania': 10},
                'build_time': 60,
                'capacity': 15,
                'name_key': 'building.tent.upgrade.manor'
            }
        ],
        'name_key': 'building.tent.name'
    },

    'lumber_camp': {
        'base_cost': {'drewno': 20},
        'build_time': 5,
        'base_workers': 2,
        'allowed_terrain': ['las'],
        'base_prod': {'drewno': 2},
        'upgrades': [
            {
                'cost': {'drewno': 40, 'żelazo': 10},
                'build_time': 14,
                'prod': {'drewno': 3},
                'workers': 3,
                'name_key': 'building.lumber_camp.upgrade.hand_sawmill'
            },
            {
                'cost': {'stal': 30, 'żelazo': 20},
                'build_time': 24,
                'prod': {'drewno': 4},
                'workers': 4,
                'name_key': 'building.lumber_camp.upgrade.steam_sawmill'
            },
            {
                'cost': {'stal': 60, 'cukier': 10},
                'build_time': 40,
                'prod': {'drewno': 5},
                'workers': 5,
                'name_key': 'building.lumber_camp.upgrade.industrial_logging_complex'
            }
        ],
        'name_key': 'building.lumber_camp.name'
    },

    'cropland': {
        'base_cost': {'drewno': 15},
        'build_time': 4,
        'base_workers': 2,
        'allowed_terrain': ['pole'],
        'base_prod': {'żywność': 1.5},
        'upgrades': [
            {
                'cost': {'drewno': 30},
                'build_time': 15,
                'prod': {'żywność': 2},
                'workers': 3,
                'name_key': 'building.cropland.upgrade.farm'
            },
            {
                'cost': {'żelazo': 20, 'stal': 10},
                'build_time': 22,
                'prod': {'żywność': 2.5},
                'workers': 4,
                'name_key': 'building.cropland.upgrade.grain_plantation'
            },
            {
                'cost': {'stal': 40, 'cukier': 5},
                'build_time': 30,
                'prod': {'żywność': 3},
                'workers': 5,
                'name_key': 'building.cropland.upgrade.folwark_with_mill'
            }
        ],
        'name_key': 'building.cropland.name'
    },

    'hunting_camp': {
        'base_cost': {'drewno': 25},
        'build_time': 6,
        'base_workers': 2,
        'allowed_terrain': ['las', 'pole'],
        'base_prod': {'skóry': 1, 'żywność': 1},
        'upgrades': [
            {
                'cost': {'drewno': 40, 'żelazo': 15},
                'build_time': 10,
                'prod': {'skóry': 1, 'żywność': 1},
                'workers': 3,
                'name_key': 'building.hunting_camp.upgrade.shepherd_outpost'
            },
            {
                'cost': {'stal': 30},
                'build_time': 24,
                'prod': {'skóry': 1.5, 'żywność': 1.5},
                'workers': 4,
                'name_key': 'building.hunting_camp.upgrade.hide_reserve'
            },
            {
                'cost': {'stal': 50, 'cygara': 5},
                'build_time': 35,
                'prod': {'skóry': 2, 'żywność': 1.5},
                'workers': 5,
                'name_key': 'building.hunting_camp.upgrade.fur_company'
            }
        ],
        'name_key': 'building.hunting_camp.name'
    },

    'tannery': {
        'base_cost': {'drewno': 30, 'żelazo': 10},
        'build_time': 8,
        'base_workers': 2,
        'allowed_terrain': ['osada', 'dzielnica'],
        'requires_settlement': True,
        'consumes': {'skóry': 1},
        'base_prod': {'ubrania': 0.5},
        'upgrades': [
            {
                'cost': {'drewno': 50, 'stal': 15},
                'build_time': 16,
                'prod': {'ubrania': 0.6},
                'workers': 3,
                'name_key': 'building.tannery.upgrade.tailor_workshop'
            },
            {
                'cost': {'stal': 40, 'cukier': 10},
                'build_time': 27,
                'prod': {'ubrania': 0.8},
                'workers': 4,
                'name_key': 'building.tannery.upgrade.clothing_manufactory'
            },
            {
                'cost': {'stal': 80, 'cygara': 10},
                'build_time': 45,
                'prod': {'ubrania': 1},
                'workers': 5,
                'name_key': 'building.tannery.upgrade.colonial_textile_factory'
            }
        ],
        'name_key': 'building.tannery.name'
    },

    'herb_garden': {
        'base_cost': {'drewno': 20},
        'build_time': 5,
        'base_workers': 2,
        'allowed_terrain': ['pole', 'las'],
        'base_prod': {'zioła': 1},
        'upgrades': [
            {
                'cost': {'drewno': 35, 'żelazo': 10},
                'build_time': 13,
                'prod': {'zioła': 1.2},
                'workers': 3,
                'name_key': 'building.herb_garden.upgrade.botanical_garden'
            },
            {
                'cost': {'stal': 25},
                'build_time': 20,
                'prod': {'zioła': 1.4},
                'workers': 4,
                'name_key': 'building.herb_garden.upgrade.medicinal_herb_plantation'
            },
            {
                'cost': {'stal': 50, 'medykamenty': 5},
                'build_time': 43,
                'prod': {'zioła': 1.6},
                'workers': 5,
                'name_key': 'building.herb_garden.upgrade.ethnobotany_institute'
            }
        ],
        'name_key': 'building.herb_garden.name'
    },

    'herbal_clinic': {
        'base_cost': {'drewno': 40, 'żelazo': 15},
        'build_time': 10,
        'base_workers': 2,
        'allowed_terrain': ['osada', 'dzielnica'],
        'requires_settlement': True,
        'consumes': {'zioła': 1},
        'base_prod': {'medykamenty': 0.5},
        'upgrades': [
            {
                'cost': {'stal': 30},
                'build_time': 14,
                'prod': {'medykamenty': 0.6},
                'workers': 3,
                'name_key': 'building.herbal_clinic.upgrade.colonial_pharmacy'
            },
            {
                'cost': {'stal': 50, 'cukier': 10},
                'build_time': 20,
                'prod': {'medykamenty': 0.8},
                'workers': 4,
                'name_key': 'building.herbal_clinic.upgrade.pharmaceutical_laboratory'
            },
            {
                'cost': {'stal': 100, 'cygara': 15},
                'build_time': 32,
                'prod': {'medykamenty': 1},
                'workers': 5,
                'name_key': 'building.herbal_clinic.upgrade.tropical_medicine_institute'
            }
        ],
        'name_key': 'building.herbal_clinic.name'
    },

    'mine': {
        'base_cost': {'drewno': 35, 'żelazo': 15},
        'build_time': 12,
        'base_workers': 3,
        'base_prod': {'trzcina': 1},
        'allowed_terrain': ['wzniesienia'],
        'upgrades': [
            {
                'cost': {'stal': 30},
                'build_time': 16,
                'base_prod': {'trzcina': 1.2},
                'workers': 4,
                'name_key': 'building.mine.upgrade.mining_shaft'
            },
            {
                'cost': {'stal': 60, 'cukier': 5},
                'build_time': 24,
                'base_prod': {'trzcina': 1.4},
                'workers': 5,
                'name_key': 'building.mine.upgrade.deep_mine'
            },
            {
                'cost': {'stal': 100, 'cygara': 10},
                'build_time': 35,
                'base_prod': {'trzcina': 1.6},
                'workers': 7,
                'name_key': 'building.mine.upgrade.mining_combine'
            }
        ],
        'name_key': 'building.mine.name'
    },

    'field_forge': {
        'base_cost': {'drewno': 50, 'żelazo': 20},
        'build_time': 14,
        'base_workers': 3,
        'requires_settlement': True,
        'allowed_terrain': ['osada', 'dzielnica'],
        'consumes': {'węgiel': 1, 'żelazo': 1},
        'base_prod': {'stal': 0.5},
        'upgrades': [
            {
                'cost': {'stal': 40},
                'build_time': 18,
                'prod': {'stal': 0.6},
                'workers': 4,
                'name_key': 'building.field_forge.upgrade.pig_iron_smelter'
            },
            {
                'cost': {'stal': 80, 'cukier': 10},
                'build_time': 25,
                'prod': {'stal': 0.8},
                'workers': 5,
                'name_key': 'building.field_forge.upgrade.martin_furnace'
            },
            {
                'cost': {'stal': 120, 'cygara': 15},
                'build_time': 38,
                'prod': {'stal': 1},
                'workers': 6,
                'name_key': 'building.field_forge.upgrade.siemens_martin_steelworks'
            }
        ],
        'name_key': 'building.field_forge.name'
    },

    'sugarcane_plantation': {
        'base_cost': {'drewno': 30},
        'build_time': 7,
        'base_workers': 3,
        'allowed_terrain': ['pole'],
        'base_prod': {'trzcina': 1},
        'upgrades': [
            {
                'cost': {'żelazo': 25},
                'build_time': 12,
                'prod': {'trzcina': 1.2},
                'workers': 4,
                'name_key': 'building.sugarcane_plantation.upgrade.hacienda'
            },
            {
                'cost': {'stal': 40},
                'build_time': 20,
                'prod': {'trzcina': 1.4},
                'workers': 5,
                'name_key': 'building.sugarcane_plantation.upgrade.sugar_latifundium'
            },
            {
                'cost': {'stal': 80, 'cygara': 10},
                'build_time': 30,
                'prod': {'trzcina': 1.6},
                'workers': 6,
                'name_key': 'building.sugarcane_plantation.upgrade.sugar_corporation'
            }
        ],
        'name_key': 'building.sugarcane_plantation.name'
    },

    'manual_sugar_mill': {
        'base_cost': {'drewno': 45, 'żelazo': 20},
        'build_time': 12,
        'base_workers': 3,
        'allowed_terrain': ['osada', 'dzielnica'],
        'requires_settlement': True,
        'consumes': {'trzcina': 2},
        'base_prod': {'cukier': 0.5},
        'upgrades': [
            {
                'cost': {'stal': 40},
                'build_time': 16,
                'prod': {'cukier': 0.6},
                'workers': 4,
                'name_key': 'building.manual_sugar_mill.upgrade.sugar_refinery'
            },
            {
                'cost': {'stal': 70, 'cukier': 10},
                'build_time': 24,
                'prod': {'cukier': 0.7},
                'workers': 5,
                'name_key': 'building.manual_sugar_mill.upgrade.steam_sugar_distillery'
            },
            {
                'cost': {'stal': 110, 'cygara': 15},
                'build_time': 36,
                'prod': {'cukier': 0.8},
                'workers': 6,
                'name_key': 'building.manual_sugar_mill.upgrade.industrial_sugar_distillery'
            }
        ],
        'name_key': 'building.manual_sugar_mill.name'
    },

    'tobacco_plantation': {
        'base_cost': {'drewno': 35},
        'build_time': 8,
        'base_workers': 3,
        'allowed_terrain': ['pole'],
        'base_prod': {'tytoń': 1},
        'upgrades': [
            {
                'cost': {'żelazo': 30},
                'build_time': 13,
                'prod': {'tytoń': 1.2},
                'workers': 4,
                'name_key': 'building.tobacco_plantation.upgrade.estancia'
            },
            {
                'cost': {'stal': 50},
                'build_time': 20,
                'prod': {'tytoń': 1.4},
                'workers': 5,
                'name_key': 'building.tobacco_plantation.upgrade.tobacco_latifundium'
            },
            {
                'cost': {'stal': 90, 'cygara': 10},
                'build_time': 32,
                'prod': {'tytoń': 1.6},
                'workers': 6,
                'name_key': 'building.tobacco_plantation.upgrade.tobacco_consortium'
            }
        ],
        'name_key': 'building.tobacco_plantation.name'
    },

    'tobacco_drying_house': {
        'base_cost': {'drewno': 50, 'żelazo': 25},
        'build_time': 14,
        'base_workers': 3,
        'requires_settlement': True,
        'consumes': {'tytoń': 1},
        'base_prod': {'cygara': 0.5},
        'allowed_terrain': ['osada', 'dzielnica'],
        'upgrades': [
            {
                'cost': {'stal': 45},
                'build_time': 18,
                'prod': {'cygara': 0.6},
                'workers': 4,
                'name_key': 'building.tobacco_drying_house.upgrade.cigar_manufactory'
            },
            {
                'cost': {'stal': 80, 'cukier': 15},
                'build_time': 26,
                'prod': {'cygara': 0.7},
                'workers': 5,
                'name_key': 'building.tobacco_drying_house.upgrade.handmade_cigar_factory'
            },
            {
                'cost': {'stal': 130, 'cygara': 20},
                'build_time': 40,
                'prod': {'cygara': 0.8},
                'workers': 6,
                'name_key': 'building.tobacco_drying_house.upgrade.premium_cigar_factory'
            }
        ],
        'name_key': 'building.tobacco_drying_house.name'
    },

    'harbor': {
        'base_cost': {'drewno': 60, 'żelazo': 30},
        'build_time': 16,
        'base_workers': 2,
        'base_prod': {'żywność': 2},
        'requires_adjacent_settlement': True,
        'allowed_terrain': ['morze'],
        'upgrades': [],
        'name_key': 'building.harbor.name'
    },

    'district': {
        'base_cost': {'drewno': 120, 'żelazo': 60, 'stal': 20},
        'build_time': 25,
        'base_workers': 5,
        'requires_adjacent_settlement': True,
        'allowed_terrain': ['las', 'pole', 'wzniesienia'],
        'upgrades': [],
        'name_key': 'building.district.name'
    }
}

RESOURCES = ["żywność", "drewno", "skóry", "ubrania", "zioła", "medykamenty", "żelazo", "stal", "trzcina", "cukier", "tytoń", "cygara", "węgiel", "srebro", "złoto", "dukaty"]
MINE_RESOURCES = ["węgiel", "żelazo", "srebro", "złoto"]
MINE_COLORS = {"węgiel": "#000000", "żelazo": "#8B0000", "srebro": "#C0C0C0", "złoto": "#FFD700"}
MINE_NAMES = {"węgiel": "Węgiel", "żelazo": "Żelazo", "srebro": "Srebro", "złoto": "Złoto"}
BASE_COLORS = {"morze": "#0066CC", "pole": "#CCCC99", "las": "#228B22", "wzniesienia": "#8B4513", "osada": "#000000", "dzielnica": "#333333"}

# Misje królewskie
ROYAL_MISSIONS = [{'base': {'drewno': 300},
  'name_key': 'royal_mission.drewno_na_stocznie.name',
  'desc_key': 'royal_mission.drewno_na_stocznie.desc'},
 {'base': {'żywność': 300, 'skóry': 50},
  'name_key': 'royal_mission.zywnosc_dla_armii.name',
  'desc_key': 'royal_mission.zywnosc_dla_armii.desc'},
 {'base': {'żelazo': 100},
  'name_key': 'royal_mission.zelazo_na_dziaa.name',
  'desc_key': 'royal_mission.zelazo_na_dziaa.desc'},
 {'base': {'stal': 60, 'drewno': 200},
  'name_key': 'royal_mission.stal_dla_floty.name',
  'desc_key': 'royal_mission.stal_dla_floty.desc'},
 {'base': {'cukier': 200},
  'name_key': 'royal_mission.cukier_dla_dworu.name',
  'desc_key': 'royal_mission.cukier_dla_dworu.desc'},
 {'base': {'złoto': 50, 'cygara': 30, 'srebro': 100},
  'name_key': 'royal_mission.prezent_dla_krola.name',
  'desc_key': 'royal_mission.prezent_dla_krola.desc'},
 {'base': {'złoto': 100},
  'name_key': 'royal_mission.zoto_dla_skarbu.name',
  'desc_key': 'royal_mission.zoto_dla_skarbu.desc'},
 {'base': {'stal': 50, 'ubrania': 100},
  'name_key': 'royal_mission.wsparcie_dla_armii.name',
  'desc_key': 'royal_mission.wsparcie_dla_armii.desc'},
 {'base': {'zioła': 50, 'medykamenty': 70},
  'name_key': 'royal_mission.zapomoga_na_choroby.name',
  'desc_key': 'royal_mission.zapomoga_na_choroby.desc'},
 {'base': {'złoto': 30, 'srebro': 50, 'żywność': 100},
  'name_key': 'royal_mission.wsparcie_koscioa.name',
  'desc_key': 'royal_mission.wsparcie_koscioa.desc'}]

NATIVE_MISSIONS_DETAILS = [{'base': {'żywność': 30, 'żelazo': 20},
  'name_key': 'native_mission.pomoc_w_polowaniu_na_bizony.name',
  'desc_key': 'native_mission.pomoc_w_polowaniu_na_bizony.desc'},
 {'base': {'cukier': 20, 'cygara': 20, 'żywność': 30},
  'name_key': 'native_mission.duchy_przodkow_sa_godne.name',
  'desc_key': 'native_mission.duchy_przodkow_sa_godne.desc'},
 {'base': {'stal': 15, 'żelazo': 30},
  'name_key': 'native_mission.biali_z_ponocy_pala_wioski.name',
  'desc_key': 'native_mission.biali_z_ponocy_pala_wioski.desc'},
 {'base': {'zioła': 30, 'medykamenty': 20},
  'name_key': 'native_mission.szaman_potrzebuje_zio.name',
  'desc_key': 'native_mission.szaman_potrzebuje_zio.desc'},
 {'base': {'ubrania': 60},
  'name_key': 'native_mission.kobiety_chca_pieknych_tkanin_od_bladych_twarzy.name',
  'desc_key': 'native_mission.kobiety_chca_pieknych_tkanin_od_bladych_twarzy.desc'},
 {'base': {'żelazo': 20, 'stal': 15},
  'name_key': 'native_mission.wodzowi_ukradli_konia.name',
  'desc_key': 'native_mission.wodzowi_ukradli_konia.desc'},
 {'base': {'złoto': 10, 'srebro': 30},
  'name_key': 'native_mission.wielki_duch_pragnie_byszczacych_kamieni.name',
  'desc_key': 'native_mission.wielki_duch_pragnie_byszczacych_kamieni.desc'},
 {'base': {'cukier': 20, 'żywność': 50},
  'name_key': 'native_mission.rum_i_cukier_na_swieto_tanca_sonca.name',
  'desc_key': 'native_mission.rum_i_cukier_na_swieto_tanca_sonca.desc'},
 {'base': {'medykamenty': 15, 'zioła': 30, 'żywność': 40},
  'name_key': 'native_mission.dzieci_choruja.name',
  'desc_key': 'native_mission.dzieci_choruja.desc'},
 {'base': {'ubrania': 30, 'żelazo': 20, 'cygara': 15},
  'name_key': 'native_mission.handel.name',
  'desc_key': 'native_mission.handel.desc'},
 {'base': {'żywność': 50, 'zioła': 20},
  'name_key': 'native_mission.susza_na_preriach.name',
  'desc_key': 'native_mission.susza_na_preriach.desc'},
 {'base': {'żywność': 40, 'cygara': 20},
  'name_key': 'native_mission.wojownicy_wracaja_z_wyprawy.name',
  'desc_key': 'native_mission.wojownicy_wracaja_z_wyprawy.desc'},
 {'base': {'drewno': 60, 'żelazo': 15},
  'name_key': 'native_mission.naprawa_palisady_wioski.name',
  'desc_key': 'native_mission.naprawa_palisady_wioski.desc'},
 {'base': {'skóry': 40, 'ubrania': 20},
  'name_key': 'native_mission.nowe_tipi_na_zime.name',
  'desc_key': 'native_mission.nowe_tipi_na_zime.desc'},
 {'base': {'złoto': 5, 'srebro': 15, 'cygara': 10},
  'name_key': 'native_mission.swieto_nadania_imienia_nowemu_wodzowi.name',
  'desc_key': 'native_mission.swieto_nadania_imienia_nowemu_wodzowi.desc'},
 {'base': {'stal': 20, 'żelazo': 20},
  'name_key': 'native_mission.konskie_stado_potrzebuje_podkow.name',
  'desc_key': 'native_mission.konskie_stado_potrzebuje_podkow.desc'},
 {'base': {'żywność': 30, 'medykamenty': 15},
  'name_key': 'native_mission.zaginieni_mysliwi.name',
  'desc_key': 'native_mission.zaginieni_mysliwi.desc'},
 {'base': {'srebro': 30, 'zioła': 10},
  'name_key': 'native_mission.srebro_na_groby_przodkow.name',
  'desc_key': 'native_mission.srebro_na_groby_przodkow.desc'},
 {'base': {'dukaty': 40, 'ubrania': 25},
  'name_key': 'native_mission.biali_handlarze_oszukali_naszych_starszych.name',
  'desc_key': 'native_mission.biali_handlarze_oszukali_naszych_starszych.desc'},
 {'base': {'drewno': 50, 'żywność': 20, 'cygara': 10},
  'name_key': 'native_mission.ogien_w_swietym_gaju.name',
  'desc_key': 'native_mission.ogien_w_swietym_gaju.desc'}]

EUROPE_PRICES = {
    "żywność": 1, "drewno": 8, "skóry": 4, "ubrania": 15,
    "zioła": 1, "medykamenty": 4, "trzcina": 6, "cukier": 12, "tytoń": 8, "cygara": 15,
    "żelazo": 10, "stal": 20, "złoto": 50, "srebro": 30, "węgiel": 3
}

BLOCK_EUROPE_BUY = {"srebro", "złoto", "trzcina", "tytoń"}

NATIVE_PRICES = {
    "żywność": 8, "drewno": 2, "skóry": 3, "ubrania": 8, "trzcina": 3, "cukier": 12, "tytoń": 5, "cygara": 15,
    "zioła": 5, "medykamenty": 15,
    "żelazo": 5, "stal": 8, "złoto": 3, "srebro": 2, "węgiel": 1

}

# towary zabronione do kupna od Indian
BLOCK_NATIVE_BUY = {"medykamenty", "ubrania", "cygara", "cukier", "stal"}

TRIBES = ["Irokezi", "Czirokezi", "Apacze", "Siuksowie", "Krikowie", "Huronowie"]

# ============== PRODUKCJA INDIAN ==============
# min/max dziennej produkcji oraz min/max pojemności magazynu (na plemię)
NATIVE_RESOURCE_ECONOMY = {
    "żywność":   {"daily_prod": (5, 10),   "stockpile": (300, 500)},
    "skóry":     {"daily_prod": (3, 5),   "stockpile": (150, 300)},
    "drewno":    {"daily_prod": (5, 10),   "stockpile": (200, 400)},
    "zioła":     {"daily_prod": (3, 5),   "stockpile": (150, 300)},
    "trzcina":   {"daily_prod": (3, 5),   "stockpile": (100, 200)},
    "tytoń":    {"daily_prod": (3, 5),   "stockpile": (50, 100)},
    "węgiel":    {"daily_prod": (1, 3),   "stockpile": (50, 100)},
    "żelazo":    {"daily_prod": (1, 3),   "stockpile": (50, 100)},
    "srebro":    {"daily_prod": (0.5, 2),   "stockpile": (30, 50)},
    "złoto":     {"daily_prod": (0.5, 1),   "stockpile": (30, 50)},
    # itd., tylko dla tych zasobów które realnie mają sens u plemion
}
# Mapping internal resource ids to localization keys
RESOURCE_DISPLAY_KEYS = {'cukier': 'res.sugar',
 'cygara': 'res.cigars',
 'drewno': 'res.wood',
 'dukaty': 'res.ducats',
 'medykamenty': 'res.meds',
 'skóry': 'res.skins',
 'srebro': 'res.silver',
 'stal': 'res.steel',
 'trzcina': 'res.cane',
 'tytoń': 'res.tobacco',
 'ubrania': 'res.clothes',
 'węgiel': 'res.coal',
 'zioła': 'res.herbs',
 'złoto': 'res.gold',
 'żelazo': 'res.iron',
 'żywność': 'res.food'}

# Mapping tribe internal names to localization keys
TRIBE_DISPLAY_KEYS = {'Apacze': 'tribe.apache',
 'Czirokezi': 'tribe.cherokee',
 'Huronowie': 'tribe.huron',
 'Irokezi': 'tribe.iroquois',
 'Krikowie': 'tribe.creek',
 'Siuksowie': 'tribe.sioux'}
