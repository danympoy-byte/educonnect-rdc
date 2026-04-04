// Données officielles des 60 provinces éducationnelles de la RDC
// Source: https://edu-nc.gouv.cd/provinces-educationnelles

export const INTRO_TEXT = `Le Ministère de l'Éducation nationale et Nouvelle Citoyenneté est constitué de 60 provinces éducationnelles réparties dans les 26 provinces administratives de la RDC. Chaque province éducationnelle est composée de sous-divisions, des antennes DINACOPE, des antennes SERNIE, des antennes de la DIGE pour les statistiques scolaires, des antennes pour le service d'orientation scolaire et professionnelle, des pools primaires et secondaires, des coordinations et des conseilleries.`;

export const COMITE_PROVINCIAL = [
  {
    role: "PROVED",
    numero: 1,
    description: "Le PROVED est le représentant du Ministre au niveau provincial ; il veille au bon fonctionnement de toutes les sous-divisions et autres structures du Ministère de l'EDU-NC de son ressort."
  },
  {
    role: "IPP",
    numero: 2,
    description: "L'IPP est le 2e responsable du Ministère de l'Éducation nationale et Nouvelle Citoyenneté au niveau provincial. Il est chargé de toutes les épreuves certificatives de son ressort."
  },
  {
    role: "DIPROCOPE",
    numero: 3,
    description: "La DIPROCOPE est le 3e responsable du Ministère de l'Éducation nationale et Nouvelle Citoyenneté au niveau provincial. Elle s'occupe de la paie des enseignants et agents des bureaux gestionnaires de son ressort."
  }
];

export const PROVINCES_EDUCATIONNELLES = [
  {
    provinceAdmin: "Bas-Uélé",
    provincesEdu: [
      {
        nom: "Bas-Uele",
        chefLieu: "BUTA",
        contacts: {
          proved: { nom: "MASUDI BIN SULUBIKA", email: "proved_basuele@minepst.gouv.cd" },
          ipp: { nom: "YAKUSU TUTA Samuel Polydor", email: "ipp_basuele@minepst.gouv.cd" },
          diprocope: { nom: "LOKOSHO MIAKA", email: "diprocope_basuele@minepst.gouv.cd" }
        },
        sousDivisions: [
          { nom: "BUTA", lieu: "BUTA" },
          { nom: "AKETI", lieu: "AKETI" },
          { nom: "ANGO", lieu: "ANGO" },
          { nom: "BONDO", lieu: "BONDO" },
          { nom: "DINGILA", lieu: "DINGILA" },
          { nom: "POKO", lieu: "POKO" }
        ]
      }
    ]
  },
  {
    provinceAdmin: "Equateur",
    provincesEdu: [
      {
        nom: "Equateur 1",
        chefLieu: "MBANDAKA",
        contacts: {
          proved: { nom: "NLANDU KABUIKU Noël", email: "proved_equateur1@minepst.gouv.cd" },
          ipp: { nom: "KIDIATA MANESA KAFUTI", email: "ipp_equateur1@minepst.gouv.cd" },
          diprocope: { nom: "MANGALA ITIWAU", email: "diprocope_equateur1@minepst.gouv.cd" }
        },
        sousDivisions: [
          { nom: "MBANDAKA 1", lieu: "N° 33 BOSOMI" },
          { nom: "MBANDAKA 2", lieu: "N° AV DE LA JUSTICE" },
          { nom: "MBANDAKA 3", lieu: "CECLI WENDJI" },
          { nom: "MBANDAKA 4", lieu: "BOLOMBO" },
          { nom: "BIKORO 1", lieu: "BIKORO CENTRE" },
          { nom: "BIKORO 2", lieu: "MC ITIPO" },
          { nom: "BIKORO 3", lieu: "KALAMBA" },
          { nom: "BIKORO 4", lieu: "MC IBOKO" },
          { nom: "INGENDE 1", lieu: "INGENDE CENTRE" },
          { nom: "INGENDE 2", lieu: "EUNGU" },
          { nom: "INGENDE 3", lieu: "BOKATOLA" },
          { nom: "INGENDE 4", lieu: "BELONDO" },
          { nom: "INGENDE 5", lieu: "LOTUMBE" },
          { nom: "LUKOLELA 1", lieu: "LUKOLELA CENTRE" },
          { nom: "LUKOLELA 2", lieu: "NKOLOLINGAMBA" },
          { nom: "LUKOLELA 3", lieu: "NGOMBE" },
          { nom: "LUKOLELA 4", lieu: "BOBANGA" },
          { nom: "BOMONGO 1", lieu: "BOMONGO CENTRE" },
          { nom: "BOMONGO 2", lieu: "LILANGA" },
          { nom: "BOMONGO 3", lieu: "BOKONDO" },
          { nom: "BOMONGO 4", lieu: "BUBURU" },
          { nom: "BOMONGO 5", lieu: "BOSOBELE" },
          { nom: "BOMONGO 6", lieu: "LIBAYA" }
        ]
      },
      {
        nom: "Equateur 2",
        chefLieu: "BASANKUSU",
        contacts: {
          proved: { nom: "BANGAMBA BADIBANGA", email: "proved_equateur2@minepst.gouv.cd" },
          ipp: { nom: "DJAMBA LUNGE Albert", email: "ipp_equateur2@minepst.gouv.cd" },
          diprocope: { nom: "MINGA MINGA", email: "diprocope_equateur2@minepst.gouv.cd" }
        },
        sousDivisions: [
          { nom: "BASANKUSU 1", lieu: "BASANKUSU CENTRE" },
          { nom: "BASANKUSU 2", lieu: "DJOMBO" },
          { nom: "BASANKUSU 3", lieu: "WAKA" },
          { nom: "BASANKUSU 4", lieu: "MPELENGE" },
          { nom: "BASANKUSU 5", lieu: "KODORO" },
          { nom: "BOLOMBA 1", lieu: "BOLOMBA CENTRE" },
          { nom: "BOLOMBA 2", lieu: "MC BOKOTE" },
          { nom: "BOLOMBA 3", lieu: "LOLANGA" },
          { nom: "BOLOMBA 4", lieu: "DJOA" },
          { nom: "BOLOMBA 5", lieu: "MANKANZA 4" },
          { nom: "BOLOMBA 6", lieu: "BONGBONGA" },
          { nom: "MANKANZA 1", lieu: "MANKANZA CENTRE" },
          { nom: "MANKANZA 2", lieu: "MOBEKA" },
          { nom: "MANKANZA 3", lieu: "BOLOMBO" },
          { nom: "MANKANZA 4", lieu: "BONGINDA" }
        ]
      }
    ]
  },
  {
    provinceAdmin: "Haut-Katanga",
    provincesEdu: [
      {
        nom: "Haut-Katanga 1",
        chefLieu: "LUBUMBASHI",
        contacts: {
          proved: { nom: "MUINKEU TSHIEND Joseph", tel: "+243 977299708", email: "proved_hautkatanga1@minepst.gouv.cd" },
          ipp: { nom: "KOKUMBO EGBA ZOYEKPETONA", email: "ipp_hautkatanga1@minepst.gouv.cd" },
          diprocope: { nom: "MALEBE LINGONDO", tel: "+243 810401506", email: "diprocope_hautkatanga1@minepst.gouv.cd" }
        },
        sousDivisions: [
          { nom: "LUBUMBASHI 1", lieu: "LUBUMBASHI" },
          { nom: "LUBUMBASHI 2", lieu: "LUBUMBASHI" },
          { nom: "LUBUMBASHI 3", lieu: "LUBUMBASHI" },
          { nom: "LUBUMBASHI 4", lieu: "LUBUMBASHI" },
          { nom: "LUBUMBASHI 5", lieu: "LUBUMBASHI" },
          { nom: "KIPUSHI", lieu: "KIPUSHI" },
          { nom: "SAKANIA", lieu: "KASUMBALESA" },
          { nom: "LUKASI 1", lieu: "LUKASI" },
          { nom: "LUKASI 2", lieu: "LUKASI" },
          { nom: "KAMBOVE", lieu: "KAMBOVE" }
        ]
      },
      {
        nom: "Haut-Katanga 2",
        chefLieu: "PWETO",
        contacts: {
          proved: { nom: "NTUMBA KABUYA Fiston", email: "proved_hautkatanga2@minepst.gouv.cd" },
          ipp: { nom: "KOY LUSANG Willy", email: "ipp_hautkatanga2@minepst.gouv.cd" },
          diprocope: { nom: "KAZADI MPYANA", email: "diprocope_hautkatanga2@minepst.gouv.cd" }
        },
        sousDivisions: [
          { nom: "PWETO", lieu: "PWETO" },
          { nom: "KILWA", lieu: "KILWA" },
          { nom: "MITWABA", lieu: "MITWABA" },
          { nom: "KASENGA", lieu: "KASENGA" }
        ]
      }
    ]
  },
  {
    provinceAdmin: "Haut-Lomami",
    provincesEdu: [
      {
        nom: "Haut-Lomami 1",
        chefLieu: "KAMINA",
        contacts: {
          proved: { nom: "SABITI KABOYO Alfred", email: "proved_hautlomami1@minepst.gouv.cd" },
          ipp: { nom: "KANKU KANDE Claude", email: "ipp_hautlomami1@minepst.gouv.cd" },
          diprocope: { nom: "MUHINDO KAPITULA", email: "diprocope_hautlomami1@minepst.gouv.cd" }
        },
        sousDivisions: [
          { nom: "KAMINA 1", lieu: "KAMINA" },
          { nom: "KAMINA 2", lieu: "KIBULA" },
          { nom: "KAMINA 3", lieu: "KIPUKWE" },
          { nom: "KANIAMA 1", lieu: "KANIAMA" },
          { nom: "KANIAMA 2", lieu: "KIMPANGA" },
          { nom: "KABONGO 1", lieu: "LUBYAY" },
          { nom: "KABONGO 2", lieu: "KITENGE" },
          { nom: "KABONGO 3", lieu: "KABOTO" },
          { nom: "KABONGO 4", lieu: "BUDI" },
          { nom: "KAYAMBA 1", lieu: "KAMAY" },
          { nom: "KAYAMBA 2", lieu: "MWALA" },
          { nom: "KYONDO KIAMBIDI", lieu: "NSOMPE" }
        ]
      },
      {
        nom: "Haut-Lomami 2",
        chefLieu: "BUKAMA",
        contacts: {
          proved: { nom: "BABANGA MBONGO Gaston", email: "proved_hautlomami2@minepst.gouv.cd" },
          ipp: { nom: "UTSHUDI OLELA Emile", email: "ipp_hautlomami2@minepst.gouv.cd" },
          diprocope: { nom: "KUAKU MBANDA", email: "diprocope_hautlomami2@minepst.gouv.cd" }
        },
        sousDivisions: [
          { nom: "BUKAMA 1", lieu: "BUKAMA" },
          { nom: "BUKAMA 2", lieu: "KIPAMBA" },
          { nom: "BUKAMA 3", lieu: "KABONDO" },
          { nom: "BUKAMA 4", lieu: "LUENA" },
          { nom: "MALEMBA-NKULU 1", lieu: "MALEMBA" },
          { nom: "MALEMBA-NKULU 2", lieu: "MULONGO" },
          { nom: "MALEMBA-NKULU 3", lieu: "MUKANGA" },
          { nom: "MALEMBA-NKULU 4", lieu: "LWAMBA" }
        ]
      }
    ]
  },
  {
    provinceAdmin: "Haut-Uélé",
    provincesEdu: [
      {
        nom: "Haut-Uele 1",
        chefLieu: "ISIRO",
        contacts: {
          proved: { nom: "ILANGA WANDA Christian", email: "proved_hautuele1@minepst.gouv.cd" },
          ipp: { nom: "NKUNAYABO MITANDA Paul", email: "ipp_hautuele1@minepst.gouv.cd" },
          diprocope: { nom: "LISONGOMI OLELA", email: "diprocope_hautuele1@minepst.gouv.cd" }
        },
        sousDivisions: [
          { nom: "ISIRO", lieu: "ISIRO CENTRE" },
          { nom: "WAMBA 1", lieu: "MALEMBA" },
          { nom: "WAMBA 2", lieu: "WAMBA" },
          { nom: "RUNGU", lieu: "ISIRO/RUNGU" },
          { nom: "NIANGARA", lieu: "NIANGARA" }
        ]
      },
      {
        nom: "Haut-Uele 2",
        chefLieu: "WATSHA",
        contacts: {
          proved: { nom: "DJABIRI ASANI Alfred", email: "proved_hautuele2@minepst.gouv.cd" },
          ipp: { nom: "KPANDJANGA MBUTCHU Jean-Christophe", email: "ipp_hautuele2@minepst.gouv.cd" },
          diprocope: { nom: "EBWA NGONDOLA", email: "diprocope_hautuele2@minepst.gouv.cd" }
        },
        sousDivisions: [
          { nom: "DUNGU", lieu: "MALEMBA" },
          { nom: "FARADJE 1", lieu: "MALEMBA" },
          { nom: "FARADJE 2", lieu: "MALEMBA" },
          { nom: "WATSA", lieu: "MALEMBA" }
        ]
      }
    ]
  },
  {
    provinceAdmin: "Ituri",
    provincesEdu: [
      {
        nom: "Ituri 1",
        chefLieu: "BUNIA",
        contacts: {
          proved: { nom: "MUKE ABASEL Yvon", email: "proved_ituri1@minepst.gouv.cd" },
          ipp: { nom: "MBAKAKA MBANGA Sébastien", email: "ipp_ituri1@minepst.gouv.cd" },
          diprocope: { nom: "SHAMAMBA MUNYAKAZI", email: "diprocope_ituri1@minepst.gouv.cd" }
        },
        sousDivisions: [
          { nom: "BUNIA", lieu: "BUNIA" },
          { nom: "IRUMU 1", lieu: "IRUMU" },
          { nom: "IRUMU 2", lieu: "BOGORO" },
          { nom: "IRUMU 3", lieu: "BETY" },
          { nom: "DJUNGU 1", lieu: "DJUNGU" },
          { nom: "DJUNGU 2", lieu: "KPANDROMA" },
          { nom: "NIZI", lieu: "NIZI" },
          { nom: "MAMBASA 1", lieu: "MAMBASA" },
          { nom: "MAMBASA 2", lieu: "BIAKATO" },
          { nom: "MAMBASA 3", lieu: "NIA-NIA" }
        ]
      },
      {
        nom: "Ituri 2",
        chefLieu: "ARU",
        contacts: {
          proved: { nom: "SHALUMOO TSAMBALI Salomon", email: "proved_ituri2@minepst.gouv.cd" },
          ipp: { nom: "MALENGA BOPE Onésime", email: "ipp_ituri2@minepst.gouv.cd" },
          diprocope: { nom: "BOLEKO EMBETA", email: "diprocope_ituri2@minepst.gouv.cd" }
        },
        sousDivisions: [
          { nom: "ARU", lieu: "ARU" },
          { nom: "ADRANGA", lieu: "ADRANGA" },
          { nom: "ARIWARA", lieu: "ARIWARA" },
          { nom: "ATSINIA", lieu: "ATSINIA" },
          { nom: "INGBOKOLO", lieu: "INGBOKOLO" },
          { nom: "LUNDI", lieu: "LUNDI" },
          { nom: "MADO", lieu: "MADO" },
          { nom: "ONDELEA", lieu: "ONDELEA" },
          { nom: "YUKU", lieu: "YUKU" }
        ]
      },
      {
        nom: "Ituri 3",
        chefLieu: "MAHAGI",
        contacts: {
          proved: { nom: "TSHIBANDA TSHIBANDA", tel: "+243 818969638", email: "proved_ituri3@minepst.gouv.cd" },
          ipp: { nom: "LONGWA MAKONGA MUBA Joseph", email: "ipp_ituri3@minepst.gouv.cd" },
          diprocope: { nom: "PAKABOMBA BASIKA", email: "diprocope_ituri3@minepst.gouv.cd" }
        },
        sousDivisions: [
          { nom: "MAHAGI 1", lieu: "MAHAGI" },
          { nom: "MAHAGI 2", lieu: "NYALEBE" },
          { nom: "MAHAGI 3", lieu: "NGOTE" },
          { nom: "MAHAGI 4", lieu: "ANGUMU" },
          { nom: "MAHAGI 5", lieu: "NDRELE" },
          { nom: "MAHAGI 6", lieu: "AUNGBA" },
          { nom: "MAHAGI 7", lieu: "DJEGU" },
          { nom: "MAHAGI 8", lieu: "NIOKA" }
        ]
      }
    ]
  },
  {
    provinceAdmin: "Kasai",
    provincesEdu: [
      {
        nom: "Kasai 1",
        chefLieu: "TSHIKAPA",
        contacts: {
          proved: { nom: "ALEMBE MBILINGA Virginie", email: "proved_kasai1@minepst.gouv.cd" },
          ipp: { nom: "YOKA ANGWEY Cyprien", email: "ipp_kasai1@minepst.gouv.cd" },
          diprocope: { nom: "DUNDA MUMAMA", email: "diprocope_kasai1@minepst.gouv.cd" }
        },
        sousDivisions: [
          { nom: "TSHIKAPA 1", lieu: "MBUMBA" },
          { nom: "TSHIKAPA 2", lieu: "DIBUMBA 1" },
          { nom: "BIAKABOMBA", lieu: "BIAKABOMBA" },
          { nom: "KABAMBAIE", lieu: "MBAWU" },
          { nom: "KAMONIA", lieu: "KAMONIA" },
          { nom: "KAMUESHA", lieu: "KAMUESHA" },
          { nom: "KANZALA", lieu: "KANZALA" },
          { nom: "KATANGA", lieu: "KATANGA" },
          { nom: "KITANGUA", lieu: "KITANGUA" },
          { nom: "LUNYEKA", lieu: "LUNYEKA" },
          { nom: "MUTENA", lieu: "MUTENA" },
          { nom: "NYANGA", lieu: "NYANGA" },
          { nom: "SHAMBUANDA", lieu: "SHAMBUANDA" },
          { nom: "LUEBO 2", lieu: "DJOKO PUNDA" },
          { nom: "LUEBO 3", lieu: "KABEMBA" }
        ]
      },
      {
        nom: "Kasai 2",
        chefLieu: "MWEKA",
        contacts: {
          proved: { nom: "BABISHA NTWARANYI Jean-Pierre", tel: "+243 994161128", email: "proved_kasai2@minepst.gouv.cd" },
          ipp: { nom: "NGWABA MABWANDAKA", email: "ipp_kasai2@minepst.gouv.cd" },
          diprocope: { nom: "BANJANA MUILA MUINDILAYI", email: "diprocope_kasai2@minepst.gouv.cd" }
        },
        sousDivisions: [
          { nom: "LUEBO 1", lieu: "LUEBO CENTRE" },
          { nom: "ILEBO 1", lieu: "ILEBO CENTRE" },
          { nom: "ILEBO 2", lieu: "MAPANGU" },
          { nom: "ILEBO 3", lieu: "MIBALAYI" },
          { nom: "SUD BANGA", lieu: "BANGA CENTRE" },
          { nom: "DEKESE 1", lieu: "DEKESE ETAT" },
          { nom: "DEKESE 2", lieu: "IDUMBE" },
          { nom: "DEKESE 3", lieu: "ISANDJA" },
          { nom: "DEKESE 4", lieu: "ANGA" },
          { nom: "DOMIONGO", lieu: "DOMIONGO" },
          { nom: "KAKENGE", lieu: "KAKENGE" },
          { nom: "KAMPUNGU", lieu: "BAKATOMBE" },
          { nom: "MISUMBA", lieu: "MISUMBA" },
          { nom: "MWEKA", lieu: "MWEKA" }
        ]
      }
    ]
  },
  {
    provinceAdmin: "Kasai-Central",
    provincesEdu: [
      {
        nom: "Kasai Central 1",
        chefLieu: "KANANGA",
        contacts: {
          proved: { nom: "MPAMPANYE BOMBOKO Richard", email: "proved_kasaicentral1@minepst.gouv.cd" },
          ipp: { nom: "MAKASINGA A GIMONDO Majel", email: "ipp_kasaicentral1@minepst.gouv.cd" },
          diprocope: { nom: "NGOTOTA MUKENGESHAYI", email: "diprocope_kasaicentral1@minepst.gouv.cd" }
        },
        sousDivisions: [
          { nom: "KANANGA 1", lieu: "KANANGA" },
          { nom: "KANANGA 2", lieu: "KATOKA" },
          { nom: "DIBAYA 1", lieu: "TSHIMBULU" },
          { nom: "DIBAYA 2", lieu: "TSHIKULA" },
          { nom: "DIBAYA 3", lieu: "KAMPONDE" },
          { nom: "DEMBA 1", lieu: "TERRITOIRE" },
          { nom: "DEMBA 2", lieu: "BENELEKA" },
          { nom: "DIMBELENGE 1", lieu: "TERRITOIRE" },
          { nom: "DIMBELENGE 2", lieu: "MASHALA" },
          { nom: "DIMBELENGE 3", lieu: "KASONGA MULE" },
          { nom: "LUBUNGA", lieu: "LUBUNGA" },
          { nom: "MUNKAMBA", lieu: "MUNKAMBA" }
        ]
      },
      {
        nom: "Kasai Central 2",
        chefLieu: "LUIZA",
        contacts: {
          proved: { nom: "KAPENDE TSHIABANGANI Tresor", tel: "+243 827783551", email: "proved_kasaicentral2@minepst.gouv.cd" },
          ipp: { nom: "MANGI BAYOBO Didier", tel: "+243 817353168", email: "ipp_kasaicentral2@minepst.gouv.cd" },
          diprocope: { nom: "MOKA MALOANI", email: "diprocope_kasaicentral2@minepst.gouv.cd" }
        },
        sousDivisions: [
          { nom: "LUIZA 1", lieu: "LUIZA CENTRE" },
          { nom: "LUIZA 2", lieu: "YAO" },
          { nom: "LUIZA 3", lieu: "LUAMBO" },
          { nom: "LUIZA 4", lieu: "MASUIKA" },
          { nom: "KAZUMBA CENTRE", lieu: "KAZUMBA" },
          { nom: "KAZUMBA NORD 1", lieu: "TSHIBALA" },
          { nom: "KAZUMBA NORD 2", lieu: "KALOMBA" },
          { nom: "KAZUMBA SUD 1", lieu: "TSHIBALA" },
          { nom: "KAZUMBA SUD 2", lieu: "BULUNGU" }
        ]
      }
    ]
  },
  {
    provinceAdmin: "Kasai-Oriental",
    provincesEdu: [
      {
        nom: "Kasai-Oriental 1",
        chefLieu: "MBUJI-MAYI",
        contacts: {
          proved: { nom: "KAPITA MPONGO", tel: "+243 995333296", email: "proved_kasaioriental1@minepst.gouv.cd" },
          ipp: { nom: "MBUYU MULUME Etienne", email: "ipp_kasaioriental1@minepst.gouv.cd" },
          diprocope: { nom: "KASUMBA KAOMBA", tel: "+243 815122836", email: "diprocope_kasaioriental1@minepst.gouv.cd" }
        },
        sousDivisions: [
          { nom: "MBUJIMAYI 1", lieu: "MBUJIMAYI" },
          { nom: "MBUJIMAYI 2", lieu: "MBUJIMAYI" },
          { nom: "MBUJIMAYI 3", lieu: "MBUJIMAYI" },
          { nom: "TSHILINGE 1", lieu: "TSHILENGE" },
          { nom: "TSHILINGE 2", lieu: "LUKALABA" },
          { nom: "KATENDA 1", lieu: "KATANDA" },
          { nom: "KATENDA 2", lieu: "TSHITENGE" },
          { nom: "LUPATAPATA", lieu: "TSHIBOMBO" }
        ]
      },
      {
        nom: "Kasai-Oriental 2",
        chefLieu: "KABEYA KAMWANGA",
        contacts: {
          proved: { nom: "MVUNZI MBEMBA Jean Marie", email: "proved_kasaioriental2@minepst.gouv.cd" },
          ipp: { nom: "LUPUTA KATEPA Lazard", email: "ipp_kasaioriental2@minepst.gouv.cd" },
          diprocope: { nom: "MUPANGILAYI MULOMBO", tel: "+243 854785746", email: "diprocope_kasaioriental2@minepst.gouv.cd" }
        },
        sousDivisions: [
          { nom: "KABEYA KAMWANGA 1", lieu: "KEENA NKUNA" },
          { nom: "KABEYA KAMWANGA 2", lieu: "MUNKAMBA" },
          { nom: "MIABI 1", lieu: "MIABI" },
          { nom: "MIABI 2", lieu: "TSHIJIBA" }
        ]
      }
    ]
  },
  {
    provinceAdmin: "Kinshasa",
    provincesEdu: [
      {
        nom: "Lukunga",
        chefLieu: "GOMBE",
        contacts: {
          proved: { nom: "MUDE NKOKO Wivine", email: "proved_kinlukunga@minepst.gouv.cd" },
          ipp: { nom: "LUMBALA KADIATA Vital", email: "ipp_kinlukunga@minepst.gouv.cd" },
          diprocope: { nom: "MPOMBO NDENGI", email: "diprocope_kinlukunga@minepst.gouv.cd" }
        },
        sousDivisions: [
          { nom: "GOMBE", lieu: "Gombe" },
          { nom: "KINTAMBO", lieu: "Kintambo" },
          { nom: "NGALIEMA 1", lieu: "Ngaliema" },
          { nom: "NGALIEMA 2", lieu: "Ngaliema" },
          { nom: "NGALIEMA 3", lieu: "Ngaliema" },
          { nom: "NGALIEMA 4", lieu: "Ngaliema" },
          { nom: "MONT NGAFULA 1", lieu: "Mont-Ngafula" },
          { nom: "MONT NGAFULA 2", lieu: "Mont-Ngafula" },
          { nom: "MONT NGAFULA 3", lieu: "Mont-Ngafula" },
          { nom: "KINSHASA", lieu: "Kinshasa" },
          { nom: "BARUMBU 1", lieu: "Barumbu" },
          { nom: "BARUMBU 2", lieu: "Barumbu" },
          { nom: "LINGWALA", lieu: "Lingwala" }
        ]
      },
      {
        nom: "Funa",
        chefLieu: "KASAVUBU",
        contacts: {
          proved: { nom: "KAMUANGA MULOWYI Bruno", email: "proved_kinfuna@minepst.gouv.cd" },
          ipp: { nom: "MAMBELE INDWO-TENE Agathe", email: "ipp_kinfuna@minepst.gouv.cd" },
          diprocope: { nom: "KUMINGA MIKOBI", email: "diprocope_kinfuna@minepst.gouv.cd" }
        },
        sousDivisions: [
          { nom: "BANDALUNGWA", lieu: "BANDALUNGWA" },
          { nom: "BUMBU 1", lieu: "BUMBU" },
          { nom: "BUMBU 2", lieu: "BUMBU" },
          { nom: "KALAMU 1", lieu: "KALAMU" },
          { nom: "KALAMU 2", lieu: "KALAMU" },
          { nom: "KASA VUBU", lieu: "KASA VUBU" },
          { nom: "MAKALA", lieu: "MAKALA" },
          { nom: "NGIRI NGIRI 1", lieu: "NGIRI NGIRI" },
          { nom: "NGIRI NGIRI 2", lieu: "NGIRI NGIRI" },
          { nom: "SELEMBAO 1", lieu: "SELEMBAO" },
          { nom: "SELEMBAO 2", lieu: "SELEMBAO" },
          { nom: "SELEMBAO 3", lieu: "SELEMBAO" }
        ]
      },
      {
        nom: "Mont-Amba",
        chefLieu: "LIMETE",
        contacts: {
          proved: { nom: "NAMBUY MAKENGO Astride", tel: "+243 820894119", email: "proved_kinmontamba@minepst.gouv.cd" },
          ipp: { nom: "TSHISEKEDI SHAMBUYI Jean", email: "ipp_kinmontamba@minepst.gouv.cd" },
          diprocope: { nom: "MASAMBA MASAMBA", email: "diprocope_kinmontamba@minepst.gouv.cd" }
        },
        sousDivisions: [
          { nom: "KINSENSO 1", lieu: "KINSENSO" },
          { nom: "KINSENSO 2", lieu: "KINSENSO" },
          { nom: "LEMBA 1", lieu: "LEMBA" },
          { nom: "LEMBA 2", lieu: "LEMBA" },
          { nom: "LIMETE 1", lieu: "LIMETE" },
          { nom: "LIMETE 2", lieu: "LIMETE" },
          { nom: "LIMETE 3", lieu: "LIMETE" },
          { nom: "MATETE 1", lieu: "MATETE" },
          { nom: "MATETE 2", lieu: "MATETE" },
          { nom: "NGABA", lieu: "NGABA" }
        ]
      },
      {
        nom: "Tshangu",
        chefLieu: "NDJILI",
        contacts: {
          proved: { nom: "TSHIABU KALONGA Liberata", tel: "+243 903487667", email: "proved_kintshangu@minepst.gouv.cd" },
          ipp: { nom: "DIANGENDA SAMUNKINDA Joseph", email: "ipp_kintshangu@minepst.gouv.cd" },
          diprocope: { nom: "MWANZA MUFONKOL", email: "diprocope_kintshangu@minepst.gouv.cd" }
        },
        sousDivisions: [
          { nom: "KIMBANSEKE 1", lieu: "Ep2 Kingasani, Q/King 1" },
          { nom: "KIMBANSEKE 2", lieu: "Institut Botosi, Q/Kakuti" },
          { nom: "KIMBANSEKE 3", lieu: "Institut Zola Emile, Q/Kutu" },
          { nom: "KIMBANSEKE 4", lieu: "EPA.1,2,3 Mokali, Q/Mokali" },
          { nom: "KIMBANSEKE 5", lieu: "Colg Mikondo, Q/Ngampani" },
          { nom: "MASINA 1", lieu: "MASINA" },
          { nom: "MASINA 2", lieu: "MASINA" },
          { nom: "MASINA 3", lieu: "MASINA" },
          { nom: "N'DJILI 1", lieu: "N'DJILI" },
          { nom: "N'DJILI 2", lieu: "N'DJILI" }
        ]
      },
      {
        nom: "Plateau",
        chefLieu: "N'SELE",
        contacts: {
          proved: { nom: "KONAPUNGU PERO Delphin", email: "proved_kinplateau@minepst.gouv.cd" },
          ipp: { nom: "NTUKADI VUNDA Bienvenu", email: "ipp_kinplateau@minepst.gouv.cd" },
          diprocope: { nom: "NDJIMI MONSHEPOLE", email: "diprocope_kinplateau@minepst.gouv.cd" }
        },
        sousDivisions: [
          { nom: "N'SELE 1", lieu: "N'SELE" },
          { nom: "N'SELE 2", lieu: "N'SELE" },
          { nom: "N'SELE 3", lieu: "N'SELE" },
          { nom: "N'SELE 4", lieu: "N'SELE" },
          { nom: "MALUKU 1", lieu: "MALUKU" },
          { nom: "MALUKU 2", lieu: "MALUKU" },
          { nom: "MALUKU 3", lieu: "MALUKU" },
          { nom: "MALUKU 4", lieu: "MALUKU" }
        ]
      }
    ]
  },
  {
    provinceAdmin: "Kongo-Central",
    provincesEdu: [
      {
        nom: "Kongo-Central 1",
        chefLieu: "MATADI",
        contacts: {
          proved: { nom: "BPROTO MASAWA Marie Salomé", email: "proved_kongocentral1@minepst.gouv.cd" },
          ipp: { nom: "MPIA WEMBA Jacques", email: "ipp_kongocentral1@minepst.gouv.cd" },
          diprocope: { nom: "LANGI BAMOSE", email: "diprocope_kongocentral1@minepst.gouv.cd" }
        },
        sousDivisions: [
          { nom: "MATADI 1", lieu: "MVUZI" },
          { nom: "MATADI 2", lieu: "VILLE BASE" },
          { nom: "BOMA", lieu: "BOMA/NZADI" },
          { nom: "MOANDA 1", lieu: "CITE DE MOANDA" },
          { nom: "MOANDA 2", lieu: "BOMA BUNGU" },
          { nom: "LUKULA 1", lieu: "LUKULA" },
          { nom: "LUKULA 2", lieu: "LUKULA" },
          { nom: "TSHELA 1", lieu: "TERRITOIRE" },
          { nom: "TSHELA 2", lieu: "MBANGA" },
          { nom: "SEKE BANZA 1", lieu: "KINZAU MVUETE" },
          { nom: "SEKE BANZA 2", lieu: "CHEF LIEU" }
        ]
      },
      {
        nom: "Kongo-Central 2",
        chefLieu: "MBANZA-NGUNGU",
        contacts: {
          proved: { nom: "MUKINYI MAVA Dieu donné", email: "proved_kongocentral2@minepst.gouv.cd" },
          ipp: { nom: "ATANDJO ONOKOKO Véronique", tel: "+243 820006207", email: "ipp_kongocentral2@minepst.gouv.cd" },
          diprocope: { nom: "PEMBE LUBUELA", email: "diprocope_kongocentral2@minepst.gouv.cd" }
        },
        sousDivisions: [
          { nom: "MBANZA NGUNGU 1", lieu: "MBANZA NGUNGU" },
          { nom: "MBANZA NGUNGU 2", lieu: "KWILU NGONGO" },
          { nom: "LUOZI 1", lieu: "LUOZI" },
          { nom: "LUOZI 2", lieu: "TADI" },
          { nom: "SONGOLOLO 1", lieu: "KIMPESE" },
          { nom: "SONGOLOLO 2", lieu: "SONGOLOLO" }
        ]
      },
      {
        nom: "Kongo-Central 3",
        chefLieu: "INKISI",
        contacts: {
          proved: { nom: "INKULA ABAL Anaclet", email: "proved_kongocentral3@minepst.gouv.cd" },
          ipp: { nom: "KINZINI SIMAY Rolland", email: "ipp_kongocentral3@minepst.gouv.cd" },
          diprocope: { nom: "BOMPONGO BOSENGE", email: "diprocope_kongocentral3@minepst.gouv.cd" }
        },
        sousDivisions: [
          { nom: "MADIMBA 1", lieu: "INKISI" },
          { nom: "MADIMBA 2", lieu: "KIMPEMBA" },
          { nom: "KASANGULU", lieu: "KASANGULU" },
          { nom: "KIMVULA", lieu: "KIMVULA" }
        ]
      }
    ]
  },
  {
    provinceAdmin: "Kwango",
    provincesEdu: [
      {
        nom: "Kwango 1",
        chefLieu: "KENGE",
        contacts: {
          proved: { nom: "OTIWI NKUNGINDÉ Ambroisine", email: "proved_kwango1@minepst.gouv.cd" },
          ipp: { nom: "KABAKISA MUKENE Simon Pierre", email: "ipp_kwango1@minepst.gouv.cd" },
          diprocope: { nom: "FALANGA GITUMBA GASAW", email: "diprocope_kwango1@minepst.gouv.cd" }
        },
        sousDivisions: [
          { nom: "FESHI 1", lieu: "FESHI CITE" },
          { nom: "FESHI 2", lieu: "MUKOSO" },
          { nom: "GANAKETI", lieu: "MWELA LEMBWA" },
          { nom: "LOBO", lieu: "LOBO" },
          { nom: "KENGE 1", lieu: "KENGE 1" },
          { nom: "KENGE 2", lieu: "KENGE 2" },
          { nom: "KIMBAU", lieu: "KIMBAU" },
          { nom: "KOBO", lieu: "KOBO" },
          { nom: "KOLOKOSO", lieu: "KOLOKOSO" },
          { nom: "PONT KWANGO", lieu: "PONT KWANGO" },
          { nom: "POPOKABAKA 1", lieu: "POPOKABAKA CITE" },
          { nom: "POPOKABAKA 2", lieu: "IPONGI" },
          { nom: "POPOKABAKA 3", lieu: "INTENGA" },
          { nom: "POPOKABAKA 4", lieu: "KABAMA" },
          { nom: "POPOKABAKA 5", lieu: "KIAMVU KINZADI" }
        ]
      },
      {
        nom: "Kwango 2",
        chefLieu: "KASONGO LUNDA",
        contacts: {
          proved: { nom: "MUSHIKO PALATA Mathieu", tel: "+243 828365556", email: "proved_kwango2@minepst.gouv.cd" },
          ipp: { nom: "MPIA ELIMA Guyguy", email: "ipp_kwango2@minepst.gouv.cd" },
          diprocope: { nom: "IWAWA NGWAMASHI", email: "diprocope_kwango2@minepst.gouv.cd" }
        },
        sousDivisions: [
          { nom: "KAHEMBA 1", lieu: "KAHEMBA CITE" },
          { nom: "KAHEMBA 2", lieu: "KULINJI" },
          { nom: "KAHEMBA 3", lieu: "MWAMUSHIKO" },
          { nom: "KASA", lieu: "MUKUNZI" },
          { nom: "KASONGO LUNDA 1", lieu: "KASONGO LUNDA CITE" },
          { nom: "KASONGO LUNDA 2", lieu: "TEMBO" },
          { nom: "KIBUNDA", lieu: "NZAMBA" },
          { nom: "KINGULU", lieu: "KINGULU" },
          { nom: "KINGWANGALA", lieu: "KINGWANGALA" },
          { nom: "MAWANGA", lieu: "MAWANGA" },
          { nom: "PANZI", lieu: "PANZI" },
          { nom: "SWA_TENDA", lieu: "KITENDA" }
        ]
      }
    ]
  },
  {
    provinceAdmin: "Kwilu",
    provincesEdu: [
      {
        nom: "Kwilu 1",
        chefLieu: "BANDUNDU-VILLE",
        contacts: {
          proved: { nom: "MUNGETA MAKULEA Hervé", email: "proved_kwilu1@minepst.gouv.cd" },
          ipp: { nom: "PAKU DITUBANZA Paul", email: "ipp_kwilu1@minepst.gouv.cd" },
          diprocope: { nom: "PEMBE NGONGA", tel: "+243 822007007", email: "diprocope_kwilu1@minepst.gouv.cd" }
        },
        sousDivisions: [
          { nom: "BANDUNDU", lieu: "BANDUNDU VILLE" },
          { nom: "BAGATA 1", lieu: "BAGATA CITE" },
          { nom: "BAGATA 2", lieu: "FATUNDU" },
          { nom: "BAGATA 3", lieu: "MPO ETAT" },
          { nom: "BAGATA 4", lieu: "MANZASAY" },
          { nom: "BULUNGU 3", lieu: "DJUMA" }
        ]
      },
      {
        nom: "Kwilu 2",
        chefLieu: "KIKWIT",
        contacts: {
          proved: { nom: "YOY BOKETE JEAN-PIERRE", email: "proved_kwilu2@minepst.gouv.cd" },
          ipp: { nom: "DJUMA TIBAMWENDA Jacques", email: "ipp_kwilu2@minepst.gouv.cd" },
          diprocope: { nom: "MANSIYONSO KUBATILA", tel: "+243 998123878", email: "diprocope_kwilu2@minepst.gouv.cd" }
        },
        sousDivisions: [
          { nom: "BULUNGU 1", lieu: "BULUNGU" },
          { nom: "BULUNGU 2", lieu: "NKARA" },
          { nom: "BULUNGU 4", lieu: "DWE" },
          { nom: "BULUNGU 5", lieu: "ZABA" },
          { nom: "BULUNGU 6", lieu: "LUSANGA" },
          { nom: "BULUNGU 7", lieu: "KIKOTI" },
          { nom: "BULUNGU 8", lieu: "MIKWI" },
          { nom: "KIKWIT 1", lieu: "KIKWIT" },
          { nom: "KIKWIT 2", lieu: "KIKWIT" },
          { nom: "KIKWIT 3", lieu: "KIKWIT" },
          { nom: "KIKWIT 4", lieu: "KIKWIT" },
          { nom: "KINZENGA", lieu: "MASAMUNA" },
          { nom: "KITOY", lieu: "KIKOY" },
          { nom: "MASI-MANIMBA 1", lieu: "MASI" },
          { nom: "MASI-MANIMBA 2", lieu: "PAY-KONGILA" },
          { nom: "MASI-MANIMBA 3", lieu: "LETA" },
          { nom: "MASI-MANIMBA 4", lieu: "MOSANGO" },
          { nom: "MOKAMO", lieu: "MOKAMO" },
          { nom: "MUTELO", lieu: "MUTELO" }
        ]
      },
      {
        nom: "Kwilu 3",
        chefLieu: "IDIOFA-CENTRE",
        contacts: {
          proved: { nom: "MATSORO LENGE Olivier", email: "proved_kwilu3@minepst.gouv.cd" },
          ipp: { nom: "MUTOMBO WA MULENJI Roger", email: "ipp_kwilu3@minepst.gouv.cd" },
          diprocope: { nom: "BAKOLA DZANGO", email: "diprocope_kwilu3@minepst.gouv.cd" }
        },
        sousDivisions: [
          { nom: "IDIOFA CENTRE", lieu: "IDIOFA CENTRE" },
          { nom: "BANDA", lieu: "BANDA" },
          { nom: "BULWEM", lieu: "BULWEM" },
          { nom: "KALO", lieu: "KALO" },
          { nom: "KIPUKU", lieu: "KIPUKU" },
          { nom: "MANGAI", lieu: "MANGAI" },
          { nom: "MATEKO", lieu: "MATEKO" },
          { nom: "DIBAYA-LUBWE", lieu: "DIBAYA" },
          { nom: "OBALA", lieu: "OBALA" },
          { nom: "GUNGU 1", lieu: "GUNGU CITE" },
          { nom: "GUNGU 2", lieu: "MUKEDI" },
          { nom: "GUNGU 3", lieu: "KANDALA" },
          { nom: "GUNGU 4", lieu: "KABUDI" },
          { nom: "GUNGU 5", lieu: "KAKOBOLA" },
          { nom: "GUNGU 6", lieu: "KILEMBE" }
        ]
      }
    ]
  },
  {
    provinceAdmin: "Lomami",
    provincesEdu: [
      {
        nom: "Lomami 1",
        chefLieu: "KABINDA",
        contacts: {
          proved: { nom: "LOBO MIKOBO", tel: "+243 829246872", email: "proved_lomami1@minepst.gouv.cd" },
          ipp: { nom: "MASIKA KATSUMIRWAKI Jeanne", email: "ipp_lomami1@minepst.gouv.cd" },
          diprocope: { nom: "MUSONGO GIDIATI", email: "diprocope_lomami1@minepst.gouv.cd" }
        },
        sousDivisions: [
          { nom: "KABINDA URBAIN", lieu: "KABINDA" },
          { nom: "KABINDA 2", lieu: "KIPUSHYA" },
          { nom: "KABINDA 3", lieu: "KAMENDE" },
          { nom: "BALUBA LUBANGULE", lieu: "KALONDA" },
          { nom: "LUDIMBI LUKULA", lieu: "MIOMBE MUAVI" },
          { nom: "VUNAYI", lieu: "MUAMBA MITANTA" },
          { nom: "LUBAO 1", lieu: "LUBAO" },
          { nom: "LUBAO 2", lieu: "KAMANA" },
          { nom: "LUBAO 3", lieu: "TSHOFA" },
          { nom: "KISENGWA", lieu: "MULENDA" },
          { nom: "NGANDAJIKA 3", lieu: "KANANGA" }
        ]
      },
      {
        nom: "Lomami 2",
        chefLieu: "NGANDAJIKA",
        contacts: {
          proved: { nom: "AGALEA MAKUNDU", tel: "+243 854750362", email: "proved_lomami2@minepst.gouv.cd" },
          ipp: { nom: "SEDEKE KATALAY Godéfroid", email: "ipp_lomami2@minepst.gouv.cd" },
          diprocope: { nom: "OMATETE LUSHIMA", email: "diprocope_lomami2@minepst.gouv.cd" }
        },
        sousDivisions: [
          { nom: "NGANDAJIKA 1", lieu: "NGANDAJIKA" },
          { nom: "NGANDAJIKA 2", lieu: "BAKUA MULUMBA" },
          { nom: "MUENE-DITU", lieu: "MUENE-DITU" },
          { nom: "LUILU 1", lieu: "LUPUTA" },
          { nom: "LUILU 2", lieu: "MULUNDU" },
          { nom: "LUILU 3", lieu: "KAMANDA KADILE" },
          { nom: "KANINTSHIN", lieu: "WIKONG" },
          { nom: "KAMIJI", lieu: "TSHISANGU" }
        ]
      }
    ]
  },
  {
    provinceAdmin: "Lualaba",
    provincesEdu: [
      {
        nom: "Lualaba 1",
        chefLieu: "KOLWEZI",
        contacts: {
          proved: { nom: "MUKUBU WA NKAMBA Bonaventure", tel: "+243 997147455", email: "proved_lualaba1@minepst.gouv.cd" },
          ipp: { nom: "LUSIENE IKOM Innocent", email: "ipp_lualaba1@minepst.gouv.cd" },
          diprocope: { nom: "OKENDE MADRAKELE", tel: "+243 810599048", email: "diprocope_lualaba1@minepst.gouv.cd" }
        },
        sousDivisions: [
          { nom: "KOLWEZI 1", lieu: "C/DILALA" },
          { nom: "KOLWEZI 2", lieu: "C/MANIKA" },
          { nom: "LUBUDI 1", lieu: "LUBUDI TERR" },
          { nom: "LUBUDI 2", lieu: "FUNGURUME" },
          { nom: "MUTSHATSHA", lieu: "MUTSHATSHA" }
        ]
      },
      {
        nom: "Lualaba 2",
        chefLieu: "KAPANGA/MUSUMBA",
        contacts: {
          proved: { nom: "KASIMPA MPWA-ANEW Déo", tel: "+243 819473042", email: "proved_lualaba2@minepst.gouv.cd" },
          ipp: { nom: "SULU KAZADI Deo Gracias", tel: "+243 814143769", email: "ipp_lualaba2@minepst.gouv.cd" },
          diprocope: { nom: "TSHINATE LUFULUABO", email: "diprocope_lualaba2@minepst.gouv.cd" }
        },
        sousDivisions: [
          { nom: "KAPANGA 1", lieu: "MUSUMBA" },
          { nom: "KAPANGA 2", lieu: "KALAMBA" },
          { nom: "KAPANGA 3", lieu: "MUSUMBA" },
          { nom: "DILOLO 1", lieu: "KASAJI" },
          { nom: "DILOLO 2", lieu: "DILOLO" },
          { nom: "SANDOA 1", lieu: "SANDOA" },
          { nom: "SANDOA 2", lieu: "KAFAKUMBA" }
        ]
      }
    ]
  },
  {
    provinceAdmin: "Mai-Ndombe",
    provincesEdu: [
      {
        nom: "Mai-Ndombe 1",
        chefLieu: "INONGO",
        contacts: {
          proved: { nom: "NZAZI NDOFULA Amos", email: "proved_maindombe1@minepst.gouv.cd" },
          ipp: { nom: "KIPOY AMWEL Marie-Claire", email: "ipp_maindombe1@minepst.gouv.cd" },
          diprocope: { nom: "POY OMATETE", email: "diprocope_maindombe1@minepst.gouv.cd" }
        },
        sousDivisions: [
          { nom: "INONGO 1", lieu: "INONGO VILLE" },
          { nom: "INONGO 2", lieu: "BANZOW MOKE" },
          { nom: "INONGO 3", lieu: "NTAND'EMBELO" },
          { nom: "INONGO 4", lieu: "MBALA" },
          { nom: "INONGO 5", lieu: "SELENGE" },
          { nom: "KIRI", lieu: "KIRI" },
          { nom: "PENDJWA", lieu: "PENDJWA" },
          { nom: "BERONGE", lieu: "BERONGE" },
          { nom: "OSHWE 1", lieu: "OSHWE" },
          { nom: "OSHWE 2", lieu: "BENA BENDI" },
          { nom: "OSHWE 3", lieu: "LOKOLAMA" },
          { nom: "OSHWE 4", lieu: "NKAW" }
        ]
      },
      {
        nom: "Mai-Ndombe 2",
        chefLieu: "BOLOBO",
        contacts: {
          proved: { nom: "ATONGBOA MADA Michel", email: "proved_maindombe2@minepst.gouv.cd" },
          ipp: { nom: "NGILENGO MUTA Noel", email: "ipp_maindombe2@minepst.gouv.cd" },
          diprocope: { nom: "MBOYO BOOLE", email: "diprocope_maindombe2@minepst.gouv.cd" }
        },
        sousDivisions: [
          { nom: "BOLOBO", lieu: "BOLOBO" },
          { nom: "KWAMOUTH", lieu: "KWAMOUTH" },
          { nom: "YUMBI", lieu: "YUMBI" }
        ]
      },
      {
        nom: "Mai-Ndombe 3",
        chefLieu: "NIOKI",
        contacts: {
          proved: { nom: "NTUMBA NDAYE Nestor", tel: "+243 812363020", email: "proved_maindombe3@minepst.gouv.cd" },
          ipp: { nom: "YEMA OLONGO OMONOMBE Jean", tel: "+243 810297359", email: "ipp_maindombe3@minepst.gouv.cd" },
          diprocope: { nom: "MUSHIMI NGOY", email: "diprocope_maindombe3@minepst.gouv.cd" }
        },
        sousDivisions: [
          { nom: "KUTU 1", lieu: "NIOKI" },
          { nom: "KUTU 2", lieu: "SEMENDUA" },
          { nom: "KUTU 3", lieu: "BOSOBE" },
          { nom: "KUTU 4", lieu: "KUTU" },
          { nom: "KUTU 5", lieu: "TOLO" },
          { nom: "KUTU 6", lieu: "BOKORO" },
          { nom: "MUSHIE 1", lieu: "MUSHIE" },
          { nom: "MUSHIE 2", lieu: "MBALI" }
        ]
      }
    ]
  },
  {
    provinceAdmin: "Maniema",
    provincesEdu: [
      {
        nom: "Maniema 1",
        chefLieu: "KINDU",
        contacts: {
          proved: { nom: "MUTOO BALINGENE Jacques", email: "proved_maniema1@minepst.gouv.cd" },
          ipp: { nom: "WHIKA YISALA Gabriel", email: "ipp_maniema1@minepst.gouv.cd" },
          diprocope: { nom: "NGANDU MUANA LUKENGU", email: "diprocope_maniema1@minepst.gouv.cd" }
        },
        sousDivisions: [
          { nom: "KASUKU", lieu: "KINDU" },
          { nom: "MIKELENGE", lieu: "KINDU" },
          { nom: "ALUNGULI", lieu: "KINDU" },
          { nom: "KAILO 1", lieu: "KAILO" },
          { nom: "KAILO 2", lieu: "KATAKO" },
          { nom: "PANGI", lieu: "KAMPENE" },
          { nom: "KALIMA", lieu: "KALIMA" },
          { nom: "PUNIA", lieu: "PUNIA" },
          { nom: "LUBUTU", lieu: "LUBUTU" }
        ]
      },
      {
        nom: "Maniema 2",
        chefLieu: "KABAMBARE",
        contacts: {
          proved: { nom: "KONGI MOGUMU Robert", email: "proved_maniema2@minepst.gouv.cd" },
          ipp: { nom: "MUDIBU KASANJI Oscar", email: "ipp_maniema2@minepst.gouv.cd" },
          diprocope: { nom: "WANGI ESOLA WALHOKO", email: "diprocope_maniema2@minepst.gouv.cd" }
        },
        sousDivisions: [
          { nom: "KABAMBARE", lieu: "KABAMBARE" },
          { nom: "LWANA", lieu: "KIBANGULA" },
          { nom: "WAMAZA", lieu: "WAMAZA" },
          { nom: "KASONGO 1", lieu: "KASONGO" },
          { nom: "KASONGO 2", lieu: "SAMBA" },
          { nom: "KASONGO 3", lieu: "MWANANDEKE" },
          { nom: "KUNDA 1", lieu: "KIPAKA" },
          { nom: "KUNDA 2", lieu: "MINGANA" },
          { nom: "KIBOMBO 1", lieu: "KIBOMBO" },
          { nom: "KIBOMBO 2", lieu: "TUNDA" }
        ]
      }
    ]
  },
  {
    provinceAdmin: "Mongala",
    provincesEdu: [
      {
        nom: "Mongala 1",
        chefLieu: "LISALA",
        contacts: {
          proved: { nom: "KILONGA KUAKATUKA Jean-Claude", email: "proved_mongala1@minepst.gouv.cd" },
          ipp: { nom: "MOMBO BANDA Francoise", email: "ipp_mongala1@minepst.gouv.cd" },
          diprocope: { nom: "MBOLISA KUMBOZINGI", email: "diprocope_mongala1@minepst.gouv.cd" }
        },
        sousDivisions: [
          { nom: "LISALA 1", lieu: "LISALA" },
          { nom: "LISALA 2", lieu: "BINGA" },
          { nom: "LISALA 3", lieu: "B/DUA" },
          { nom: "BONGANDANGA 1", lieu: "BGDBGA C" },
          { nom: "BONGANDANGA 2", lieu: "B/SIMBA" },
          { nom: "BONGANDANGA 3", lieu: "B/NZANOA" },
          { nom: "BONGANDANGA 4", lieu: "B/MELO" },
          { nom: "BONGANDANGA 5", lieu: "PIMU" }
        ]
      },
      {
        nom: "Mongala 2",
        chefLieu: "BUMBA",
        contacts: {
          proved: { nom: "SABIO TAABU ZINAWANZA", email: "proved_mongala2@minepst.gouv.cd" },
          ipp: { nom: "KPOKOLO KUFA Moise", tel: "+243 812870585", email: "ipp_mongala2@minepst.gouv.cd" },
          diprocope: { nom: "KONZINGA LANGOWE", email: "diprocope_mongala2@minepst.gouv.cd" }
        },
        sousDivisions: [
          { nom: "BUMBA 1", lieu: "BUMBA" },
          { nom: "BUMBA 2", lieu: "MONZAMBOLI" },
          { nom: "BUMBA 3", lieu: "LOLO" },
          { nom: "BUMBA 4", lieu: "YANDONGI" }
        ]
      }
    ]
  },
  {
    provinceAdmin: "Nord-Kivu",
    provincesEdu: [
      {
        nom: "Nord-Kivu 1",
        chefLieu: "GOMA",
        contacts: {
          proved: { nom: "GBAWEZA KABANGO Luc", tel: "+243 817437562", email: "proved_nordkivu1@minepst.gouv.cd" },
          ipp: { nom: "SHABISHIMBO RUSOSHA", tel: "+243 813178147", email: "ipp_nordkivu1@minepst.gouv.cd" },
          diprocope: { nom: "NTANTU MANZENZI", tel: "+243 976492533", email: "diprocope_nordkivu1@minepst.gouv.cd" }
        },
        sousDivisions: [
          { nom: "GOMA", lieu: "GOMA" },
          { nom: "HIMBI", lieu: "Q/VOLCAN/HIMBI/GOMA" },
          { nom: "KARISIMBI 1", lieu: "Q/MURARA/GOMA" },
          { nom: "KARISIMBI 2", lieu: "Q/KASIKA/GOMA" },
          { nom: "NYIRAGONGO 1", lieu: "MUNIGI" },
          { nom: "NYIRAGONGO 2", lieu: "KIBUMBA" },
          { nom: "RUTSHURU 1", lieu: "RUTSHURU CENTRE" },
          { nom: "RUTSHURU 2", lieu: "NYANZALE" },
          { nom: "RUTSHURU 3", lieu: "RUMANGABO" },
          { nom: "RUTSHURU 4", lieu: "NYAMILIMA" },
          { nom: "RUTSHURU 5", lieu: "BAMBO" }
        ]
      },
      {
        nom: "Nord-Kivu 2",
        chefLieu: "BUTEMBO",
        contacts: {
          proved: { nom: "BISIMWA BALEKEMBAKA Norbert", email: "proved_nordkivu2@minepst.gouv.cd" },
          ipp: { nom: "MASUMBUKO MUNIKE", tel: "+243 995305116", email: "ipp_nordkivu2@minepst.gouv.cd" },
          diprocope: { nom: "MANYANGA PERO", tel: "+243 994526424", email: "diprocope_nordkivu2@minepst.gouv.cd" }
        },
        sousDivisions: [
          { nom: "BENI", lieu: "BENI" },
          { nom: "BULONGO", lieu: "BULONGO" },
          { nom: "KYONDO", lieu: "KYONDO" },
          { nom: "KAMANGO", lieu: "KAMANGO" },
          { nom: "BUTEMBO 1", lieu: "BUTEMBO" },
          { nom: "BUTEMBO 2", lieu: "BUTEMBO" },
          { nom: "LUBERO 1", lieu: "LUBERO 1" },
          { nom: "LUBERO 2", lieu: "MASEREKA" },
          { nom: "KITSOMBIRO", lieu: "KITSOMBIRO" },
          { nom: "KIRUMBA", lieu: "KIRUMBA" },
          { nom: "NJIAPANDA", lieu: "NJIAPANDA" },
          { nom: "OICHA", lieu: "OICHA" }
        ]
      },
      {
        nom: "Nord-Kivu 3",
        chefLieu: "WALIKALE",
        contacts: {
          proved: { nom: "OHANU LUHAHE Pat.", email: "proved_nordkivu3@minepst.gouv.cd" },
          ipp: { nom: "LEBANGE HOWE Alain", email: "ipp_nordkivu3@minepst.gouv.cd" },
          diprocope: { nom: "KABWANGALA KHABA", tel: "+243 819583329", email: "diprocope_nordkivu3@minepst.gouv.cd" }
        },
        sousDivisions: [
          { nom: "MASISI 1", lieu: "MASISI CENTRE" },
          { nom: "MASISI 2", lieu: "SAKE" },
          { nom: "MASISI 3", lieu: "KITSHANGA" },
          { nom: "MASISI 4", lieu: "KATOYI" },
          { nom: "MASISI 5", lieu: "NGUNGU" },
          { nom: "MASISI 6", lieu: "BURUNGU" },
          { nom: "MWESO", lieu: "MWESO" },
          { nom: "BWEREMANA", lieu: "BWEREMANA" },
          { nom: "WALIKALE 1", lieu: "WALIKALE CENTRE" },
          { nom: "WALIKALE 2", lieu: "KESHEBERE" },
          { nom: "WALIKALE 3", lieu: "PINGA" },
          { nom: "WALIKALE 4", lieu: "HOMBO" }
        ]
      }
    ]
  },
  {
    provinceAdmin: "Nord-Ubangi",
    provincesEdu: [
      {
        nom: "Nord-Ubangi 1",
        chefLieu: "GBADOLITE",
        contacts: {
          proved: { nom: "MATAND TSHISH BAVUAL Urbain", email: "proved_nordubangi1@minepst.gouv.cd" },
          ipp: { nom: "BONKINDO MBOYO Benjamin", email: "ipp_nordubangi1@minepst.gouv.cd" },
          diprocope: { nom: "MOLUKA NDUMBA", email: "diprocope_nordubangi1@minepst.gouv.cd" }
        },
        sousDivisions: [
          { nom: "GBADOLITE", lieu: "GBADOLITE" },
          { nom: "BUSINGA 1", lieu: "BUSINGA" },
          { nom: "BUSINGA 2", lieu: "LOKO" },
          { nom: "BODANGABO 1", lieu: "BODANGABO" },
          { nom: "BODANGABO 2", lieu: "GBOSASA" },
          { nom: "KARAWA 1", lieu: "KAWARA" },
          { nom: "KARAWA 2", lieu: "INERA" },
          { nom: "BOSOBOLO 1", lieu: "BOSOBOLO" },
          { nom: "BOSOBOLO 2", lieu: "BILI" },
          { nom: "OTTO-MBANZA", lieu: "PAMBWA" }
        ]
      },
      {
        nom: "Nord-Ubangi 2",
        chefLieu: "YAKOMA",
        contacts: {
          proved: { nom: "KAZADI NTUMBA Matthieu", tel: "+243 817012572", email: "proved_nordubangi2@minepst.gouv.cd" },
          ipp: { nom: "MUKE IKOM EKUISSIN Baudoin", email: "ipp_nordubangi2@minepst.gouv.cd" },
          diprocope: { nom: "IBONJI MABENGU", email: "diprocope_nordubangi2@minepst.gouv.cd" }
        },
        sousDivisions: [
          { nom: "MOBAYI MBONGO 1", lieu: "MOBAYI MBONGO CENTRE" },
          { nom: "YAKOMA 1", lieu: "YAKOMA" },
          { nom: "YAKOMA 2", lieu: "ABUZI" },
          { nom: "YAKOMA 3", lieu: "WAPINDA" },
          { nom: "MONVEDA", lieu: "MONVEDA" },
          { nom: "WASOLO", lieu: "WASOLO" },
          { nom: "NDAYO", lieu: "NDAYO" },
          { nom: "KOTAKOLI", lieu: "YAKOMA/KOTAKOLI" },
          { nom: "SALONGO", lieu: "SALONGO" },
          { nom: "KANDO", lieu: "KANDO" },
          { nom: "UELE", lieu: "UELE" },
          { nom: "NZAMBA", lieu: "NZAMBA" }
        ]
      }
    ]
  },
  {
    provinceAdmin: "Sankuru",
    provincesEdu: [
      {
        nom: "Sankuru 1",
        chefLieu: "LODJA",
        contacts: {
          proved: { nom: "BOLOMA BATSUBOFEKO Gregory", email: "proved_sankuru1@minepst.gouv.cd" },
          ipp: { nom: "NKUNDA NTUMBA Sylvain", email: "ipp_sankuru1@minepst.gouv.cd" },
          diprocope: { nom: "IKALA IKALA", email: "diprocope_sankuru1@minepst.gouv.cd" }
        },
        sousDivisions: [
          { nom: "LODJA 1", lieu: "LODJA CITE" },
          { nom: "LODJA 2", lieu: "SHINGA" },
          { nom: "LODJA 3", lieu: "TOKOMBE" },
          { nom: "LODJA 4", lieu: "ONA" },
          { nom: "KATAKO-KOMBE 1", lieu: "KATAKO CITE" },
          { nom: "KATAKO-KOMBE 2", lieu: "ONEMBA" },
          { nom: "KATAKO-KOMBE 3", lieu: "WEMBO-NYAMA" },
          { nom: "KATAKO-KOMBE 4", lieu: "DJALO-NDJEKA" }
        ]
      },
      {
        nom: "Sankuru 2",
        chefLieu: "LUSAMBO",
        contacts: {
          proved: { nom: "TARA MUNGOMA Déogratias", email: "proved_sankuru2@minepst.gouv.cd" },
          ipp: { nom: "MULUMBA MUKENDI MATULU", email: "ipp_sankuru2@minepst.gouv.cd" },
          diprocope: { nom: "NKELANI MALEMBANGANZI", email: "diprocope_sankuru2@minepst.gouv.cd" }
        },
        sousDivisions: [
          { nom: "LUSAMBO 1", lieu: "LUSAMBO" },
          { nom: "LUSAMBO 2", lieu: "MUKINJI" },
          { nom: "LUBEFU 1", lieu: "LUBEFU" },
          { nom: "LUBEFU 2", lieu: "TSHUMBE" },
          { nom: "KOLE 1", lieu: "KOLE" },
          { nom: "KOLE 2", lieu: "BENA DIBELE" },
          { nom: "LOMELA", lieu: "LOMELA" }
        ]
      }
    ]
  },
  {
    provinceAdmin: "Sud-Kivu",
    provincesEdu: [
      {
        nom: "Sud-Kivu 1",
        chefLieu: "BUKAVU",
        contacts: {
          proved: { nom: "TOSWESWE LIUNDA Léon", email: "proved_sudkivu1@minepst.gouv.cd" },
          ipp: { nom: "MWAYESI BILEKA Jean", email: "ipp_sudkivu1@minepst.gouv.cd" },
          diprocope: { nom: "BUKOKO Papy", email: "diprocope_sudkivu1@minepst.gouv.cd" }
        },
        sousDivisions: [
          { nom: "BUKAVU 1", lieu: "BUKAVU MONDJE" },
          { nom: "BUKAVU 2", lieu: "BAGIRA" },
          { nom: "BUKAVU 3", lieu: "KADUTU" },
          { nom: "KABARE 1", lieu: "KABARE" },
          { nom: "KABARE 2", lieu: "MUDAKA" },
          { nom: "WALUNGU 1", lieu: "WALUNGU" },
          { nom: "WALUNGU 2", lieu: "MUGOGO" },
          { nom: "WALUNGU 3", lieu: "KANIOLA" },
          { nom: "IDJWI 1", lieu: "BOSI" },
          { nom: "IDJWI 2", lieu: "BUGARULA" },
          { nom: "KALEHE 1", lieu: "KALEHE" },
          { nom: "KALEHE 2", lieu: "MINOVA" },
          { nom: "BUNYAKIRI", lieu: "BULAMBO" }
        ]
      },
      {
        nom: "Sud-Kivu 2",
        chefLieu: "FIZI",
        contacts: {
          proved: { nom: "BOPE PIEMA Albert", email: "proved_sudkivu2@minepst.gouv.cd" },
          ipp: { nom: "INGOMO ITSWENG Médard", email: "ipp_sudkivu2@minepst.gouv.cd" },
          diprocope: { nom: "MAKYAMBI MUKONGO", email: "diprocope_sudkivu2@minepst.gouv.cd" }
        },
        sousDivisions: [
          { nom: "BARAKA", lieu: "BARAKA" },
          { nom: "FIZI 1", lieu: "FIZI CENTRE" },
          { nom: "FIZI 2", lieu: "MBOKO" },
          { nom: "FIZI 3", lieu: "MISISI" },
          { nom: "FIZI 4", lieu: "KILEMBWE" },
          { nom: "MINEMBWE", lieu: "RUNUNDU" },
          { nom: "UVIRA 1", lieu: "UVIRA" },
          { nom: "UVIRA 2", lieu: "KILOMONI" },
          { nom: "UVIRA 3", lieu: "SANGE" },
          { nom: "UVIRA 4", lieu: "KIGONGO" },
          { nom: "UVIRA 5", lieu: "MAKOBOLA" }
        ]
      },
      {
        nom: "Sud-Kivu 3",
        chefLieu: "KAMITUGA",
        contacts: {
          proved: { nom: "MUKEKWA KASHALE Narcisse", email: "proved_sudkivu3@minepst.gouv.cd" },
          ipp: { nom: "MATUBA WUNDA Léonard", email: "ipp_sudkivu3@minepst.gouv.cd" },
          diprocope: { nom: "BASALUCHI KILOSHO", email: "diprocope_sudkivu3@minepst.gouv.cd" }
        },
        sousDivisions: [
          { nom: "KAMITUGA", lieu: "KAMITUGA" },
          { nom: "KITUTU", lieu: "KITUTU" },
          { nom: "MWENGA", lieu: "MWENGA" },
          { nom: "SHABUNDA 1", lieu: "SHABUNDA" },
          { nom: "SHABUNDA 2", lieu: "LULINGU" },
          { nom: "SHABUNDA 3", lieu: "KIGULUBE" }
        ]
      }
    ]
  },
  {
    provinceAdmin: "Sud-Ubangi",
    provincesEdu: [
      {
        nom: "Sud-Ubangi 1",
        chefLieu: "GEMENA",
        contacts: {
          proved: { nom: "KABASELE TSHIWEWE Constantin", email: "proved_sudubangi1@minepst.gouv.cd" },
          ipp: { nom: "OMOY W'UKUSA Yvonne", email: "ipp_sudubangi1@minepst.gouv.cd" },
          diprocope: { nom: "BOTULI BUKELA BOOTO", email: "diprocope_sudubangi1@minepst.gouv.cd" }
        },
        sousDivisions: [
          { nom: "GEMENA 1", lieu: "GEMENA" },
          { nom: "GEMENA 2", lieu: "BOWARA" },
          { nom: "GEMENA 3", lieu: "BOKUDA" },
          { nom: "BUDJALA 1", lieu: "BUDJALA" },
          { nom: "BUDJALA 2", lieu: "NDAGE" },
          { nom: "BUDJALA 3", lieu: "BOBA" },
          { nom: "KUNGU 1", lieu: "KUNGU" },
          { nom: "KUNGU 2", lieu: "BAMOPUTA" },
          { nom: "LIBENGE 1", lieu: "LIBENGE" },
          { nom: "LIBENGE 2", lieu: "MAWUY" },
          { nom: "LIBENGE 3", lieu: "ZONGO" }
        ]
      },
      {
        nom: "Sud-Ubangi 2",
        chefLieu: "ZONGO",
        contacts: {
          proved: { nom: "TSHIBAKA KABUENA Jean-Baptiste", email: "proved_sudubangi2@minepst.gouv.cd" },
          ipp: { nom: "KIMPUMPU MUKINA Emile", email: "ipp_sudubangi2@minepst.gouv.cd" },
          diprocope: { nom: "MUKAYA TSHIBANGU", email: "diprocope_sudubangi2@minepst.gouv.cd" }
        },
        sousDivisions: [
          { nom: "ZONGO", lieu: "ZONGO" },
          { nom: "LIBENGE 1", lieu: "LIBENGE" },
          { nom: "LIBENGE 2", lieu: "MAWUYA" }
        ]
      }
    ]
  },
  {
    provinceAdmin: "Tanganyika",
    provincesEdu: [
      {
        nom: "Tanganyika 1",
        chefLieu: "KALEMIE",
        contacts: {
          proved: { nom: "BAELEAY WA BAELEAY Prince", email: "proved_tanganyika1@minepst.gouv.cd" },
          ipp: { nom: "MUNYABARENZI NZIRABASEBIA", email: "ipp_tanganyika1@minepst.gouv.cd" },
          diprocope: { nom: "MAKADI MAMBEMBE", email: "diprocope_tanganyika1@minepst.gouv.cd" }
        },
        sousDivisions: [
          { nom: "KALEMIE 1", lieu: "C/LUKUGA" },
          { nom: "KALEMIE 2", lieu: "C/TANGANYIKA" },
          { nom: "KALEMIE 3", lieu: "C/LAC" },
          { nom: "NYUNZU 1", lieu: "CITE NYUNZU" },
          { nom: "NYUNZU 2", lieu: "LUYEYE" },
          { nom: "MOBA 1", lieu: "MOBA" },
          { nom: "MOBA 2", lieu: "KASENGA" },
          { nom: "MOBA 3", lieu: "MOBE" }
        ]
      },
      {
        nom: "Tanganyika 2",
        chefLieu: "KONGOLO",
        contacts: {
          proved: { nom: "LISONZU WA LISONZU Jean-Pierre", email: "proved_tanganyika2@minepst.gouv.cd" },
          ipp: { nom: "MOTOBA SASSA Emmanuel", email: "ipp_tanganyika2@minepst.gouv.cd" },
          diprocope: { nom: "KIMBUNGU MBUNGU", email: "diprocope_tanganyika2@minepst.gouv.cd" }
        },
        sousDivisions: [
          { nom: "KONGOLO 1", lieu: "KONGOLO" },
          { nom: "KONGOLO 2", lieu: "MBUGUA" },
          { nom: "KABALO 1", lieu: "KABALO" },
          { nom: "KABALO 2", lieu: "KABULO" },
          { nom: "MANONO 1", lieu: "MANONO" },
          { nom: "MANONO 2", lieu: "ANKORO" },
          { nom: "MANONO 3", lieu: "KIAMBI" }
        ]
      }
    ]
  },
  {
    provinceAdmin: "Tshopo",
    provincesEdu: [
      {
        nom: "Tshopo 1",
        chefLieu: "KISANGANI",
        contacts: {
          proved: { nom: "MUIMBI MUIMBI Alain", email: "proved_tshopo1@minepst.gouv.cd" },
          ipp: { nom: "BISANGA NSEMBA Cyprien", email: "ipp_tshopo1@minepst.gouv.cd" },
          diprocope: { nom: "BENA KAYEMBE", email: "diprocope_tshopo1@minepst.gouv.cd" }
        },
        sousDivisions: [
          { nom: "KISANGANI 1", lieu: "KISANGANI" },
          { nom: "KISANGANI 2", lieu: "KISANGANI" },
          { nom: "KISANGANI 3", lieu: "KISANGANI" },
          { nom: "KISANGANI 4", lieu: "KISANGANI" },
          { nom: "KISANGANI 5", lieu: "KISANGANI" },
          { nom: "ISANGI 1", lieu: "ISANGI" },
          { nom: "ISANGI 2", lieu: "YANGAMBI" },
          { nom: "ISANGI 3", lieu: "YAOLWA" },
          { nom: "ISANGI 4", lieu: "YAKUSU" },
          { nom: "YAHUMA 1", lieu: "YAHUMA" },
          { nom: "YAHUMA 2", lieu: "YAHUMA" },
          { nom: "OPALA", lieu: "OPALA" }
        ]
      },
      {
        nom: "Tshopo 2",
        chefLieu: "YANGAMBI",
        contacts: {
          proved: { nom: "MOKITO GAUDA", email: "proved_tshopo2@minepst.gouv.cd" },
          ipp: { nom: "MAWANGA KUMANDAKA", email: "ipp_tshopo2@minepst.gouv.cd" },
          diprocope: { nom: "SHANGA KAPINGA", email: "diprocope_tshopo2@minepst.gouv.cd" }
        },
        sousDivisions: [
          { nom: "BASOKO 1", lieu: "BASOKO" },
          { nom: "BASOKO 2", lieu: "YALIGIMBA" },
          { nom: "BAFWASENDE 1", lieu: "BAFWASENDE" },
          { nom: "BAFWASENDE 2", lieu: "OPIENGE" },
          { nom: "BANALIA", lieu: "BANALIA" },
          { nom: "UBUNDU 1", lieu: "UBUNDU" },
          { nom: "UBUNDU 2", lieu: "LUBUNGA" },
          { nom: "UBUNDU 3", lieu: "KISANGANI" }
        ]
      }
    ]
  },
  {
    provinceAdmin: "Tshuapa",
    provincesEdu: [
      {
        nom: "Tshuapa 1",
        chefLieu: "BOENDE",
        contacts: {
          proved: { nom: "BAKOLI EFANDJOBILA Prosper", email: "proved_tshuapa1@minepst.gouv.cd" },
          ipp: { nom: "MASEY KITAKA", email: "ipp_tshuapa1@minepst.gouv.cd" },
          diprocope: { nom: "KWETE MANDJUM Léon", email: "diprocope_tshuapa1@minepst.gouv.cd" }
        },
        sousDivisions: [
          { nom: "BOENDE 1", lieu: "BOENDE" },
          { nom: "BOENDE 2", lieu: "BOENDE" },
          { nom: "MONKOTO 1", lieu: "MONKOTO" },
          { nom: "MONKOTO 2", lieu: "YOLOTA" },
          { nom: "DJOLU 1", lieu: "DJOLU" },
          { nom: "DJOLU 2", lieu: "LINGOMO" }
        ]
      },
      {
        nom: "Tshuapa 2",
        chefLieu: "BOKUNGU",
        contacts: {
          proved: { nom: "BOPE MBANTSHI Valentin", email: "proved_tshuapa2@minepst.gouv.cd" },
          ipp: { nom: "ADUMANA THOMO Etienne", email: "ipp_tshuapa2@minepst.gouv.cd" },
          diprocope: { nom: "OPIO BILEO", email: "diprocope_tshuapa2@minepst.gouv.cd" }
        },
        sousDivisions: [
          { nom: "BOKUNGU 1", lieu: "BOKUNGU" },
          { nom: "BOKUNGU 2", lieu: "YOLOMBO" },
          { nom: "BOKUNGU 3", lieu: "YANGAMBO" },
          { nom: "IKELA 1", lieu: "IKELA" },
          { nom: "IKELA 2", lieu: "MONDOMBE" },
          { nom: "IKELA 3", lieu: "IKELA" },
          { nom: "BEFALE 1", lieu: "BEFALE" },
          { nom: "BEFALE 2", lieu: "LOMELA" }
        ]
      }
    ]
  }
];

// Statistiques calculées
export const STATS = {
  totalProvincesAdmin: 26,
  totalProvincesEdu: 60,
  totalSousDivisions: PROVINCES_EDUCATIONNELLES.reduce(
    (acc, p) => acc + p.provincesEdu.reduce((a, pe) => a + pe.sousDivisions.length, 0), 0
  )
};
