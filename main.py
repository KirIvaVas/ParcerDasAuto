from bs4 import BeautifulSoup
import requests
import json
from re import compile, sub
from datetime import datetime
# import pandas as pd


url = "https://www.kleinanzeigen.de"
headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) '
                         'AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36'}
brands_section__css_locator = "#browsebox-searchform > div > " \
                             "section:nth-child(2) > div > ul"
models_s3election_css_locator = "#browsebox-searchform > div > " \
                             "section:nth-child(2) > div > ul > li > ul > li > ul"
class_brands_n_models_locator = "text-link-subdued"

ranges_dict = {
"damage": ("yes", "no"),
"fuel type": ("petrol", "diesel"),
"offer type": ("offer", "purchase"),
"additional search criteria": "",
"mileage_min": (0, 5000000),
"mileage_max": (0, 5000000),
"price_min": (0, 5000000),
"price_max": (0, 5000000),
"registration_min": (1900, datetime.now().year),
"registration_max": (1900, datetime.now().year)
}

"""
url_audi = https://www.kleinanzeigen.de/s-autos
/audi
/s-line # Поменять разделитель
/preis:2000:50000
/c216
+autos.fuel_s:diesel
+autos.km_i:5000%2C40000
+autos.marke_s:audi
+autos.model_s:a6
+autos.schaden_s:ja
"""


def brands_parcer():
    """
    Rarcers site for the brands
    :return: dict of {brand name: locator}
    """
    page_auto_text = requests.get(f"{url}/s-autos/c216", headers=headers).text
    brands_classes = BeautifulSoup(page_auto_text, "html.parser").select_one(
        brands_section__css_locator).find_all(class_=class_brands_n_models_locator)[:-1]
    return {tag.string.lower(): tag for tag in brands_classes}


def models_parcer(pb):
    """
    Models parcer
    :param pb - dict of {brand:locator}:
    :return: A dict of {brand name:models List}
    """
    models_d = {}
    for brand, brand_locator in pb.items():
        url_auto = url + brand_locator.get("href")
        page_model_text = requests.get(url_auto, headers=headers).text
        model_classes = BeautifulSoup(page_model_text,
                                      "html.parser").select_one(
            models_s3election_css_locator).find_all(
            class_=class_brands_n_models_locator)
        models_d[brand] = [model.string.lower() for model in model_classes]
    return models_d


def autos_data_reader():
    with open("autos_data.json", "r") as file:
        autos_data_str = file.read()
        data_obj = json.loads(autos_data_str)
    return data_obj


def autos_data_checker(autos_data, rd):
    def spelling_check(param, values):
        if param not in values:
            print(f"The indicated parameter \""
                  + param
                  + f"\" does not presented on the parced site. Check the "
                    f"spelling otherwise it will be ignored.")


    def range_check(param, values_range):
        min, max = values_range
        if param not in range(min, max):
            print(f"The indicated value \""
                  + str(param)
                  + f"\" does not meet the specified range. Check the "
                    f"range in README.md otherwise the value will be ignored.")

    auto_data_new = []
    for auto in autos_data:
        auto_new = {}
        for key, value in auto.items():
            str_values_list =  list(rd.keys())[:4] + list(rd.keys())[10:]
            all_models_list = []
            [all_models_list.extend(sublist) for sublist in rd["model"].values()]
            int_values_list = list(rd.keys())[4:10]
            if key in str_values_list and key != "model" and key != "additional search criteria":
                auto_new[key] = str(sub(r'[^a-zA-Z ]', '', value))\
                    .lower()\
                    .strip()
                spelling_check(auto_new[key], rd[key])

            if key == "model":
                auto_new[key] = str(sub(r'[^a-zA-Z0-9\'\- ]', '', value))\
                    .lower()\
                    .strip()
                spelling_check(auto_new[key], all_models_list)

            if key == "additional search criteria":
                auto_new[key] = str(sub(r'[^a-zA-Z0-9\'\- ]', '', value))\
                    .lower()\
                    .strip()

            if key in int_values_list:
                auto_new[key] = int(sub(r'[^0-9]', '', str(value)))
                range_check(auto_new[key], rd[key])
        auto_data_new.append(auto_new)
    print(auto_data_new)
    return auto_data_new # проверить содержит ли изменения


def url_composition(ad, pm):
    for auto in ad[1:]:
        auto_url = url
        model = ad["model"]
        if model in pm.keys():
            auto_url += model
        else:
            print("""Automobile brand is not right. Check autos_data.json 
            "marke" keys. Program is terminated.""")
            exit()


if __name__ == '__main__':
    # For the purpose of speed the part of the code below was temporary
    # disabled.
    # parcered_brands = brands_parcer()
    # parcered_models = models_parcer(parcered_brands)
    parcered_models = {'volkswagen': ['181', 'amarok', 'arteon', 'beetle', 'bora', 'caddy', 'cc', 'corrado', 'crafter', 'eos', 'fox', 'golf', 'id.3', 'id.4', 'id.5', 'id.buzz', 'iltis', 'jetta', 'käfer', 'karmann ghia', 'lt', 'lupo', 'new beetle', 'passat', 'phaeton', 'polo', 'routan', 'santana', 'scirocco', 'sharan', 't1', 't2', 't3', 't4', 't5', 't6', 't7 multivan', 'taigo', 'taro', 'tiguan', 'tiguan allspace', 'touareg', 'touran', 'vw-busse', 'up!', 'vento', 'xl1', 'weitere vw'], 'mercedes benz': ['190', '200', '220', '230', '240', '250', '260', '270', '280', '290', '300', '320', '350', '380', '400', '416', '420', '450', '500', '560', '600', 'a-klasse', 'b-klasse', 'c-klasse', 'ce-klasse', 'e-klasse', 'g-klasse', 'gla-klasse', 'glb-klasse', 'glc-klasse', 'gle-klasse', 'gls-klasse', 'gt-klasse', 'm-klasse', 'r-klasse', 's-klasse', 'slc-klasse', 'v-klasse', 'x-klasse', 'citan', 'cl', 'cla', 'clc', 'clk', 'cls', 'eqa', 'eqb', 'eqc', 'eqe', 'eqs', 'eqv', 'glk', 'gl', 'mb 100', 'sl', 'slk', 'slr', 'sls amg', 'sprinter', 'vaneo', 'vario', 'viano', 'vito', 'weitere mercedes benz'], 'bmw': ['1er', '2er', '3er', '4er', '5er', '6er', '7er', 'i3', 'i4', 'i8', 'ix', 'ix3', 'm reihe', 'x reihe', 'z reihe', '2002', '840', '850', 'weitere bmw'], 'audi': ['80', '90', '100', '200', 'a1', 'a2', 'a3', 'a4', 'a5', 'a6', 'a7', 'a8', 'a4 allroad', 'a6 allroad', 'cabriolet', 'coupe', 'e-tron', 'q2', 'q3', 'q4', 'q5', 'q7', 'q8', 'quattro', 'r8', 'rs2', 'rs3', 'rs4', 'rs5', 'rs6', 'rs7', 'rsq3', 'rsq8', 's1', 's2', 's3', 's4', 's5', 's6', 's7', 's8', 'sq2', 'sq5', 'sq7', 'sq8', 'tt', 'v8', 'weitere audi'], 'opel': ['adam', 'agila', 'ampera', 'ampera-e', 'antara', 'ascona', 'astra', 'calibra', 'campo', 'cascada', 'combo', 'combo life', 'commodore', 'corsa', 'crossland (x)', 'diplomat', 'frontera', 'grandland (x)', 'gt', 'insignia', 'insignia ct', 'kadett', 'karl', 'manta', 'meriva', 'mokka', 'mokka x', 'monterey', 'monza', 'movano', 'omega', 'rekord', 'rocks-e', 'senator', 'sintra', 'signum', 'speedster', 'tigra', 'vectra', 'vivaro', 'zafira', 'zafira life', 'zafira tourer', 'weitere opel'], 'ford': ['aerostar', 'bronco', 'b-max', 'c-max', 'capri', 'courier', 'crown', 'cougar', 'ecosport', 'econoline', 'econovan', 'escape', 'escort', 'explorer', 'edge', 'excursion', 'expedition', 'f 100', 'f 150', 'f 250', 'f 350', 'fairlane', 'falcon', 'fiesta', 'flex', 'focus', 'fusion', 'galaxy', 'granada', 'grand c-max', 'grand tourneo', 'gt', 'ka', 'kuga', 'maverick', 'mercury', 'mondeo', 'mustang', 'mustang mach-e', 'orion', 'probe', 'puma', 'ranger', 'raptor', 's-max', 'scorpio', 'sierra', 'sportka', 'streetka', 'taunus', 'taurus', 'thunderbird', 'tourneo', 'transit', 'windstar', 'weitere ford'], 'renault': ['alaskan', 'alpine a110', 'alpine a310', 'alpine v6', 'arkana', 'avantime', 'captur', 'clio', 'coupe', 'espace', 'express', 'fluence', 'fuego', 'grand espace', 'grand modus', 'grand scenic', 'kadja', 'kangoo', 'koleos', 'laguna', 'latitude', 'mascott', 'master', 'megane', 'modus', 'p 1400', 'r-reihe', 'rapid', 'safrane', 'scenic', 'spider', 'talisman', 'trafic', 'twingo', 'twizy', 'vel satis', 'wind', 'zoe', 'weitere renault'], 'skoda': ['105', '120', '135', 'citigo', 'enyaq', 'fabia', 'favorit', 'felicia', 'kamiq', 'karoq', 'kodiaq', 'octavia', 'pick-up', 'praktik', 'rapid', 'roomster', 'scala', 'superb', 'yeti', 'weitere skoda'], 'seat': ['alhambra', 'altea', 'arona', 'arosa', 'ateca', 'cordoba', 'exeo', 'ibiza', 'inca', 'leon', 'marbella', 'mii', 'tarraco', 'toledo', 'weitere seat'], 'peugeot': ['1er reihe', '2er reihe', '3er reihe', '4er reihe', '5er reihe', '6er reihe', '8er reihe', '1007', '2008', '3008', '4007', '4008', '5008', 'bipper', 'bipper tepee', 'boxer', 'expert', 'expert tepee', 'ion', 'j5', 'partner', 'partner tepee', 'rcz', 'rifter', 'tepee', 'traveller', 'weitere peugeot'], 'fiat': ['124', '124 spider', '126', '127', '130', '131', '500', '500c', '500l', '500l cross', '500l living', '500l trekking', '500l urban', '500s', '500x', 'albea', 'barchetta', 'brava', 'bravo', 'cinquecento', 'coupe', 'croma', 'dino', 'doblo', 'ducato', 'fiorino', 'freemont', 'fullback', 'grande punto', 'idea', 'linea', 'marea', 'multipla', 'new panda', 'palio', 'panda', 'punto evo', 'punto', 'qubo', 'regata', 'scudo', 'sedici', 'seicento', 'spider europa', 'strada', 'stilo', 'talento', 'tempra', 'tipo', 'ulysse', 'uno', 'x 1/9', 'weitere fiat'], 'hyundai': ['accent', 'atos', 'bayon', 'coupe', 'elantra', 'galloper', 'genesis', 'getz', 'grandeur', 'grand santa fe', 'h 100', 'h-1', 'h-1 starex', 'h350', 'ioniq', 'ioniq 5', 'i reihe', 'ix-reihe', 'kona', 'lantra', 'matrix', 'nexo', 's-coupe', 'santa', 'sonata', 'staria', 'terracan', 'trajet', 'tucson', 'veloster', 'veracruz', 'xg-reihe', 'weitere hyundai'], 'citroen': ['berlingo', '2 cv', 'ax', 'bx', 'c-crosser', 'c-elysee', 'c-zero', 'c3 aircross', 'c3 picasso', 'c4 aircross', 'c4 cactus', 'c4 picasso', 'c4 spacetourer', 'c5 aircross', 'c5 x', 'c1', 'c2', 'c3', 'c4', 'c5', 'c6', 'c8', 'cx', 'ds', 'ds3', 'ds4', 'ds4 crossback', 'ds5', 'e-mehari', 'evasion', 'grand c4 picasso / spacetourer', 'gsa', 'jumper', 'jumpy', 'nemo', 'saxo', 'sm', 'spacetourer', 'visa', 'xantia', 'xm', 'xsara', 'xsara picasso', 'zx', 'weitere citroen'], 'toyota': ['4-runner', 'auris', 'auris touring sports', 'avensis', 'avensis verso', 'aygo', 'camry', 'carina', 'celica', 'c-hr', 'corolla', 'corolla verso', 'cressida', 'crown', 'dyna', 'fj', 'gt86', 'hiace', 'hilux', 'iq', 'land cruiser', 'mirai', 'mr 2', 'paseo', 'picnic', 'previa', 'prius', 'prius+', 'proace(verso)', 'proace city', 'rav', 'sequoia', 'sienna', 'starlet', 'supra', 'tercel', 'tundra', 'urban cruiser', 'verso s', 'verso', 'yaris', 'weitere toyota'], 'mini': ['clubman', 'clubvan', 'cooper', 'countryman', 'one', 'weitere mini'], 'smart': ['crossblade', 'forfour', 'fortwo', 'roadster', 'weitere smart'], 'nissan': ['100 nx', '200 sx', '240 sx', '280 zx', '300 zx', '350z', '370z', 'almera', 'almera tino', 'altima', 'ariya', 'bluebird', 'cabstar', 'cherry', 'cube', 'e-nv200', 'evalia', 'gt-r', 'interstar', 'juke', 'king cab', 'kubistar', 'laurel', 'leaf', 'maxima', 'micra', 'murano', 'navara', 'note', 'np 300', 'nv-reihe', 'pathfinder', 'patrol', 'pickup', 'pixo', 'prairie', 'primera', 'pulsar', 'qashqai', 'qashqai+2', 'sentra', 'serena', 'silvia', 'skyline', 'sunny', 'terrano', 'tilda', 'townstar', 'trade', 'vanette', 'x-trail', 'weitere nissan'], 'mazda': ['1er reihe', '2er reihe', '3er reihe', '5er reihe', '6er reihe', '929', 'cx reihe', 'b series', 'bt-50', 'demio', 'e series', 'mpv', 'mx reihe', 'premacy', 'rx reihe', 'tribute', 'xedos', 'weitere mazda'], 'kia': ['carens', 'carnival', 'ceed', "cee'd sportswagon", 'cerato', 'clarus', 'ev6', 'joice', 'k2700', 'magentis', 'niro hybrid', 'opirus', 'optima', 'picanto', 'pregio', 'pride', 'proceed', 'rio', 'rocsta', 'sephia', 'shuma', 'sorento', 'soul', 'sportage', 'stinger', 'stonic', 'venga', 'xceed', 'weitere kia'], 'porsche': ['356', '911', '912', '914', '918', '924', '928', '944', '968', 'boxster', 'carrera gt', 'cayenne', 'cayman', 'macan', 'panamera', 'taycan', 'weitere porsche'], 'volvo': ['240', '244', '245', '262', '264', '340', '440', '460', '480', '740', '745', '760', '780', '850', '855', '940', '944', '945', '960', 's40', 's60', 's70', 's80', 's90', 'v40', 'v40 cross country', 'v50', 'v60', 'v60 cross country', 'v70', 'v90', 'v90 cross country', 'amazon', 'c reihe', 'xc reihe', 'weitere volvo'], 'dacia': ['dokker', 'duster', 'jogger', 'lodgy', 'logan', 'logan pick-up', 'pick up', 'sandero', 'spring', 'weitere dacia'], 'mitsubishi': ['300 gt', 'asx', 'canter', 'carisma', 'colt', 'diamante', 'eclipse', 'eclipse cross', 'galant', 'galloper', 'grandis', 'i-miev', 'l-reihe', 'lancer', 'mirage', 'outlander', 'pajero', 'pajero pinin', 'pick-up', 'plug-in hybrid outlander', 'sapporo', 'sigma', 'space-reihe', 'starion', 'weitere mitsubishi'], 'suzuki': ['alto', 'baleno', 'carry', 'celerio', 'grand', 'ignis', 'jimny', 'kizashi', 'liana', 'lj', 'sj samurai', 'splash', 'super-carry', 'swace', 'swift', 'sx4', 'sx4 s-cross', 'vitara', 'wagon r+', 'x-90', 'weitere suzuki'], 'chevrolet': ['2500', 'alero', 'astro', 'avalanche', 'aveo', 'beretta', 'blazer', 'c1500', 'camaro', 'caprice', 'captiva', 'cavalier', 'chevelle', 'chevy van', 'colorado', 'cruze', 'el camino', 'epica', 'evanda', 'express', 'g', 'hhr', 'impala', 'k1500', 'k30', 'kalos', 'lacetti', 'lumina', 'malibu', 'matiz', 'nubira', 'orlando', 'rezzo', 's-10', 'silverado', 'spark', 'ssr', 'suburban', 'tahoe', 'trailblazer', 'trans sport', 'trax', 'weitere chevrolet'], 'honda': ['accord', 'aerodeck', 'civic', 'concerto', 'cr reihe', 'e', 'fr-v', 'hr-v', 'insight', 'integra', 'jazz', 'legend', 'logo', 'nsx', 'odyssey', 'prelude', 's2000', 'stream', 'weitere honda'], 'land rover': ['defender', 'discovery', 'discovery sport', 'freelander', 'range rover', 'range rover evoque', 'range rover sport', 'range rover velar', 'serie 1', 'serie 2', 'serie 3', 'weitere land rover'], 'jeep': ['cherokee', 'cj', 'comanche', 'commander', 'compass', 'gladiator', 'grand', 'patriot', 'renegade', 'wagoneer', 'willys', 'wrangler', 'weitere jeep'], 'jaguar': ['daimler', 'e type', 'f type', 's type', 'x type', 'e-pace', 'f-pace', 'i-pace', 'mk ii', 'xe', 'xf', 'xj', 'xj12', 'xj40', 'xj6', 'xj8', 'xjr', 'xjs', 'xjsc', 'xk', 'xk8', 'xkr', 'weitere jaguar'], 'alfa romeo': ['145', '147', '156', '159', '4c', 'alfa 146', 'alfa 155', 'alfa 164', 'alfa 166', 'alfa 33', 'alfa 75', 'alfa 90', 'alfasud', 'alfetta', 'brera', 'corsswagon', 'giulia', 'giulietta', 'gt', 'gtv', 'junior', 'mito', 'spider', 'sprint', 'stelvio', 'weitere alfa romeo'], 'tesla': ['model s', 'model 3', 'model x', 'model y', 'roadster', 'weitere tesla'], 'subaru': ['b9 tribeca', 'brz', 'forester', 'impreza', 'justy', 'legacy', 'levorg', 'libero', 'outback', 'svx', 'trezia', 'tribeca', 'wrx sti', 'xv', 'weitere subaru'], 'chrysler': ['200', '300c', '300 m', 'aspen', 'crossfire', 'daytona', 'grand', 'imperial', 'le baron', 'neon', 'new yorker', 'pacifica', 'pt cruiser', 'saratoga', 'sebring', 'stratus', 'vision', 'voyager', 'weitere chrysler'], 'saab': ['9-3', '9-5', '9-7x', '90', '900', '9000', '96', '99', 'weitere saab'], 'trabant': ['601', 'weitere trabi'], 'daihatsu': ['applause', 'charade', 'copen', 'cuore', 'feroza/sportrak', 'freeclimber', 'gran move', 'hijet', 'materia', 'move', 'rocky/fourtrak', 'sirion', 'terios', 'trevis', 'yrv', 'weitere daihatsu'], 'lada': ['111', '1200', '2107', '2110', '2111', 'granta', 'kalina', 'niva', 'nova', 'priora', 'samara', 'taiga', 'urban', 'vesta', 'weitere lada'], 'lexus': ['ct 200h', 'es-serie', 'gs-serie', 'is 200', 'is 220', 'is 250', 'is 300', 'is 350', 'is-f', 'lc-serie', 'ls', 'nx', 'rc f', 'rc 200', 'rc 300', 'rx-serie', 'sc-serie', 'ux', 'weitere lexus'], 'lancia': ['beta', 'dedra', 'delta', 'flaminia', 'flavia', 'fulvia', 'gamma', 'kappa', 'lybra', 'musa', 'phedra', 'thema', 'thesis', 'voyager', 'ypsilon', 'zeta', 'weitere lancia'], 'rover': ['freelander', 'range rover', 'weitere rover'], 'daewoo': ['espero', 'evanda', 'kalos', 'lanos', 'lacetti', 'leganza', 'matiz', 'nubira', 'rezzo', 'tacuma', 'weitere daewoo']}
    ranges_dict["brand"] = list(parcered_models.keys())
    ranges_dict["model"] = parcered_models
    # print(ranges_dict)
    autos_data = autos_data_reader()
    autos_data_checked = autos_data_checker(autos_data, ranges_dict)

    url_list = url_composition(autos_data_checked, parcered_models)




"""
- GUI integration?
-
"""
