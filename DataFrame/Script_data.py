{
 "cells": [
  {
   "cell_type": "code",
   "execution_count": null,
   "id": "7702cc31",
   "metadata": {},
   "outputs": [],
   "source": [
    "# pip install requests\n",
    "# pip install pandas\n",
    "# pip install csv-reader\n",
    "# pip install numpy\n",
    "# pip install geopandas\n",
    "# pip install zipfile38\n",
    "# pip install os-win\n",
    "# pip install pickle5\n",
    "# pip install shutils\n",
    "\n",
    "\n",
    "\n",
    "import requests\n",
    "import pandas as pd\n",
    "import csv\n",
    "import numpy as np\n",
    "import geopandas as gpd\n",
    "import zipfile38 as zipfile\n",
    "import os\n",
    "import pickle\n",
    "import shutil\n",
    "\n",
    "# Pour télécharger la database, allez sur ce site :  \n",
    "# https://statbel.fgov.be/fr/propos-de-statbel/methodologie/classifications/geographie\n",
    "# Ensuite en bas de la page prendre 'REFNIS(CSV, 29.8 Kb)'"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": null,
   "id": "518cc026",
   "metadata": {},
   "outputs": [],
   "source": [
    "pip install shutils"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": null,
   "id": "95eb66e3",
   "metadata": {},
   "outputs": [],
   "source": [
    "f= open (r\"Belgique.csv.csv\")\n",
    "belgique= pd.read_csv(f, sep = ';')\n",
    "\n",
    "df = belgique[['Code INS','Entités administratives']]\n",
    "df.set_index('Entités administratives',inplace=True)\n",
    "\n"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": null,
   "id": "bae92df8",
   "metadata": {},
   "outputs": [],
   "source": [
    "df"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": null,
   "id": "bc241139",
   "metadata": {},
   "outputs": [],
   "source": [
    "a = input('Entrez le nom de la ville: ')\n",
    "\n",
    "def ville_INS(a):\n",
    "    objet = df.loc[[a], ['Code INS']]\n",
    "    b = objet['Code INS'].values\n",
    "     \n",
    "    return b\n",
    "\n",
    "ville_INS(a)"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": null,
   "id": "e8f54ab1",
   "metadata": {},
   "outputs": [],
   "source": [
    "nis = int(ville_INS(a))\n",
    "\n",
    "def save(nis):\n",
    "    \n",
    "    with open(f'../L72{nis}.zip', 'wb') as fp:\n",
    "        req = requests.get(f'https://eservices.minfin.fgov.be/myminfin-rest/cadastral-plan/cadastralPlan/2021/{nis}/72')\n",
    "        fp.write(req.content)\n",
    "        \n",
    "save(nis)"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": null,
   "id": "16b9c8d0",
   "metadata": {
    "scrolled": true
   },
   "outputs": [],
   "source": [
    "#Extraire uniquement les fichiers necessaires\n",
    "\n",
    "file = f'../L72{nis}.zip'\n",
    "def dezip(file):\n",
    "    with zipfile.ZipFile(file, 'r') as zip: \n",
    "        zip.extract('Bpn_CaPa.dbf', f'L72{nis}extract')\n",
    "        zip.extract('Bpn_CaPa.prj', f'L72{nis}extract')\n",
    "        zip.extract('Bpn_CaPa.shp', f'L72{nis}extract')\n",
    "        zip.extract('Bpn_CaPa.sbn', f'L72{nis}extract')\n",
    "        zip.extract('Bpn_CaPa.sbx', f'L72{nis}extract')\n",
    "        zip.extract('Bpn_CaPa.shx', f'L72{nis}extract')\n",
    "        \n",
    "        \n",
    "        zip.extract('Bpn_CaBu.shp', f'L72{nis}extract')\n",
    "        zip.extract('Bpn_CaBu.shx', f'L72{nis}extract')\n",
    "        zip.extract('Bpn_CaBu.dbf', f'L72{nis}extract')\n",
    "        zip.extract('Bpn_CaBu.prj', f'L72{nis}extract')\n",
    "        zip.extract('Bpn_CaBu.sbn', f'L72{nis}extract')\n",
    "        zip.extract('Bpn_CaBu.sbx', f'L72{nis}extract')\n",
    "        \n",
    "        \n",
    "        zip.extract('Bpn_ReBu.shp', f'L72{nis}extract')\n",
    "        zip.extract('Bpn_ReBu.shx', f'L72{nis}extract')\n",
    "        zip.extract('Bpn_ReBu.dbf', f'L72{nis}extract')\n",
    "        zip.extract('Bpn_ReBu.prj', f'L72{nis}extract')\n",
    "        zip.extract('Bpn_ReBu.sbn', f'L72{nis}extract')\n",
    "        zip.extract('Bpn_ReBu.sbx', f'L72{nis}extract')\n",
    "        \n",
    "        \n",
    "        zip.extract('Apn_CaDi.shp', f'L72{nis}extract')\n",
    "        zip.extract('Apn_CaDi.shx', f'L72{nis}extract')\n",
    "        zip.extract('Apn_CaDi.dbf', f'L72{nis}extract')\n",
    "        zip.extract('Apn_CaDi.prj', f'L72{nis}extract')\n",
    "        zip.extract('Apn_CaDi.sbn', f'L72{nis}extract')\n",
    "        zip.extract('Apn_CaDi.sbx', f'L72{nis}extract')\n",
    "    \n",
    "dezip(file)\n",
    "\n"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": null,
   "id": "e2f40bae",
   "metadata": {},
   "outputs": [],
   "source": [
    "os.mkdir(f'L72{nis}clear')"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": null,
   "id": "f04d9387",
   "metadata": {
    "scrolled": true
   },
   "outputs": [],
   "source": [
    "# Garder uniquement Capakey et geometry\n",
    "\n",
    "shapefile_CaPa = gpd.read_file(f\"./L72{nis}extract/Bpn_CaPa.shp\")\n",
    "def CaPa_New(shapefile):\n",
    "    new_shape_capa = shapefile_CaPa[['CaPaKey','geometry']]\n",
    "    output = open(f'./L72{nis}clear/Bpn_CaPa_clear.pickle','wb')\n",
    "    pickle.dump(new_shape_capa, output)\n",
    "    output.close()\n",
    "    return new_shape_capa\n",
    "\n",
    "CaPa_New(shapefile_CaPa)\n",
    "    "
   ]
  },
  {
   "cell_type": "code",
   "execution_count": null,
   "id": "8fc86858",
   "metadata": {},
   "outputs": [],
   "source": [
    "shapefile_CaBu"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": null,
   "id": "c924a95f",
   "metadata": {},
   "outputs": [],
   "source": [
    "shapefile_CaBu = gpd.read_file(f\"./L72{nis}extract/Bpn_CaBu.shp\")\n",
    "\n",
    "def CaBu_New(shapefile_CaBu):\n",
    "\n",
    "    new_shape_cabu = shapefile_CaBu[shapefile_CaBu['Type'] =='CL']\n",
    "    new_shape_cabu = new_shape_cabu[['Shape_area','geometry']]\n",
    "    output = open(f'./L72{nis}clear/Bpn_CaBu_clear.pickle','wb')\n",
    "    pickle.dump(new_shape_cabu, output)\n",
    "    output.close()\n",
    "    return new_shape_cabu\n",
    "\n",
    "CaBu_New(shapefile_CaBu)"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": null,
   "id": "e05dc8c3",
   "metadata": {},
   "outputs": [],
   "source": [
    "shapefile_ReBu = gpd.read_file(f\"./L72{nis}extract/Bpn_ReBu.shp\")\n",
    "\n",
    "def ReBu_New(shapefile_ReBu):\n",
    "    new_shape_rebu = shapefile_ReBu[['TYPE', 'geometry']]\n",
    "    output = open(f'./L72{nis}clear/Bpn_ReBu_clear.pickle','wb')\n",
    "    pickle.dump(new_shape_rebu, output)\n",
    "    output.close()\n",
    "    return new_shape_rebu\n",
    "\n",
    "ReBu_New(shapefile_ReBu)"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": null,
   "id": "fa708fba",
   "metadata": {},
   "outputs": [],
   "source": [
    "shapefile_CaDi = gpd.read_file(f\"./L72{nis}extract/Apn_CaDi.shp\")\n",
    "shapefile_CaDi\n",
    "def CaDi_New(shapefile_CaDi):\n",
    "    new_shape_cadi = shapefile_CaDi[['CaDiKey','NameDUT','geometry']]\n",
    "    output = open(f'./L72{nis}clear/Apn_CaDi_clear.pickle','wb')\n",
    "    pickle.dump(new_shape_cadi, output)\n",
    "    output.close()\n",
    "    return new_shape_cadi\n",
    "\n",
    "CaDi_New(shapefile_CaDi)"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": null,
   "id": "8e556c1e",
   "metadata": {},
   "outputs": [],
   "source": [
    "\n",
    "shutil.rmtree(f'./L72{nis}extract')\n"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": null,
   "id": "e2928f1d",
   "metadata": {},
   "outputs": [],
   "source": [
    "shutil.rmtree(f'../L72{nis}.zip', 'wb')"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": null,
   "id": "7c7e7c88",
   "metadata": {},
   "outputs": [],
   "source": []
  }
 ],
 "metadata": {
  "kernelspec": {
   "display_name": "Python 3",
   "language": "python",
   "name": "python3"
  },
  "language_info": {
   "codemirror_mode": {
    "name": "ipython",
    "version": 3
   },
   "file_extension": ".py",
   "mimetype": "text/x-python",
   "name": "python",
   "nbconvert_exporter": "python",
   "pygments_lexer": "ipython3",
   "version": "3.8.8"
  }
 },
 "nbformat": 4,
 "nbformat_minor": 5
}
