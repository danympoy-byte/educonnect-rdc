# Mapping des 60 provinces éducationnelles vers les 26 provinces administratives de la RDC

PROVINCES_EDUCATIONNELLES_VERS_ADMINISTRATIVES = {
    # Kinshasa (1 → 1)
    "Kinshasa": "Kinshasa",
    
    # Kongo Central (1 → 1)
    "Kongo Central": "Kongo Central",
    
    # Kwango (2 → 1)
    "Kwango Nord": "Kwango",
    "Kwango Sud": "Kwango",
    
    # Kwilu (3 → 1)
    "Kwilu Nord": "Kwilu",
    "Kwilu Sud": "Kwilu",
    "Kwilu Centre": "Kwilu",
    
    # Mai-Ndombe (2 → 1)
    "Mai-Ndombe Nord": "Mai-Ndombe",
    "Mai-Ndombe Sud": "Mai-Ndombe",
    
    # Équateur (3 → 1)
    "Équateur Nord": "Équateur",
    "Équateur Sud": "Équateur",
    "Équateur Centre": "Équateur",
    
    # Mongala (2 → 1)
    "Mongala Nord": "Mongala",
    "Mongala Sud": "Mongala",
    
    # Nord-Ubangi (2 → 1)
    "Nord-Ubangi Est": "Nord-Ubangi",
    "Nord-Ubangi Ouest": "Nord-Ubangi",
    
    # Sud-Ubangi (2 → 1)
    "Sud-Ubangi Nord": "Sud-Ubangi",
    "Sud-Ubangi Sud": "Sud-Ubangi",
    
    # Tshuapa (2 → 1)
    "Tshuapa Nord": "Tshuapa",
    "Tshuapa Sud": "Tshuapa",
    
    # Tshopo (3 → 1)
    "Tshopo Nord": "Tshopo",
    "Tshopo Sud": "Tshopo",
    "Tshopo Centre": "Tshopo",
    
    # Bas-Uele (2 → 1)
    "Bas-Uele Nord": "Bas-Uele",
    "Bas-Uele Sud": "Bas-Uele",
    
    # Haut-Uele (2 → 1)
    "Haut-Uele Nord": "Haut-Uele",
    "Haut-Uele Sud": "Haut-Uele",
    
    # Ituri (3 → 1)
    "Ituri Nord": "Ituri",
    "Ituri Sud": "Ituri",
    "Ituri Centre": "Ituri",
    
    # Nord-Kivu (3 → 1)
    "Nord-Kivu Nord": "Nord-Kivu",
    "Nord-Kivu Sud": "Nord-Kivu",
    "Nord-Kivu Centre": "Nord-Kivu",
    
    # Sud-Kivu (3 → 1)
    "Sud-Kivu Nord": "Sud-Kivu",
    "Sud-Kivu Sud": "Sud-Kivu",
    "Sud-Kivu Centre": "Sud-Kivu",
    
    # Maniema (2 → 1)
    "Maniema Nord": "Maniema",
    "Maniema Sud": "Maniema",
    
    # Haut-Katanga (3 → 1)
    "Haut-Katanga Nord": "Haut-Katanga",
    "Haut-Katanga Sud": "Haut-Katanga",
    "Haut-Katanga Centre": "Haut-Katanga",
    
    # Lualaba (2 → 1)
    "Lualaba Nord": "Lualaba",
    "Lualaba Sud": "Lualaba",
    
    # Tanganyika (3 → 1)
    "Tanganyika Nord": "Tanganyika",
    "Tanganyika Sud": "Tanganyika",
    "Tanganyika Centre": "Tanganyika",
    
    # Haut-Lomami (2 → 1)
    "Haut-Lomami Nord": "Haut-Lomami",
    "Haut-Lomami Sud": "Haut-Lomami",
    
    # Kasaï (2 → 1)
    "Kasaï Nord": "Kasaï",
    "Kasaï Sud": "Kasaï",
    
    # Kasaï-Central (2 → 1)
    "Kasaï-Central Nord": "Kasaï-Central",
    "Kasaï-Central Sud": "Kasaï-Central",
    
    # Kasaï-Oriental (3 → 1)
    "Kasaï-Oriental Nord": "Kasaï-Oriental",
    "Kasaï-Oriental Sud": "Kasaï-Oriental",
    "Kasaï-Oriental Centre": "Kasaï-Oriental",
    
    # Lomami (2 → 1)
    "Lomami Nord": "Lomami",
    "Lomami Sud": "Lomami",
    
    # Sankuru (2 → 1)
    "Sankuru Nord": "Sankuru",
    "Sankuru Sud": "Sankuru",
}

# Liste des 26 provinces administratives
PROVINCES_ADMINISTRATIVES = [
    "Kinshasa",
    "Kongo Central",
    "Kwango",
    "Kwilu",
    "Mai-Ndombe",
    "Équateur",
    "Mongala",
    "Nord-Ubangi",
    "Sud-Ubangi",
    "Tshuapa",
    "Tshopo",
    "Bas-Uele",
    "Haut-Uele",
    "Ituri",
    "Nord-Kivu",
    "Sud-Kivu",
    "Maniema",
    "Haut-Katanga",
    "Lualaba",
    "Tanganyika",
    "Haut-Lomami",
    "Kasaï",
    "Kasaï-Central",
    "Kasaï-Oriental",
    "Lomami",
    "Sankuru"
]

def get_province_administrative(province_educationnelle: str) -> str:
    """Retourner la province administrative correspondant à une province éducationnelle"""
    return PROVINCES_EDUCATIONNELLES_VERS_ADMINISTRATIVES.get(province_educationnelle, province_educationnelle)
