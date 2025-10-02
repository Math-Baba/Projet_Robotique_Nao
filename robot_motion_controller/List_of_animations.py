# -*- coding: utf-8 -*-
import qi

ip_robot = "11.0.0.147"
port = 9559

def save_both_formats():
    session = qi.Session()
    try:
        session.connect("tcp://{}:{}".format(ip_robot, port))
        print("Connexion réussie\n")
        
        behavior_manager = session.service("ALBehaviorManager")
        installed_behaviors = behavior_manager.getInstalledBehaviors()
        
        # Organiser par catégorie
        categories = {}
        for behavior in installed_behaviors:
            parts = behavior.split('/')
            if len(parts) > 1:
                category = '/'.join(parts[:-1])
                if category not in categories:
                    categories[category] = []
                categories[category].append(behavior)
            else:
                if 'Autres' not in categories:
                    categories['Autres'] = []
                categories['Autres'].append(behavior)
        
        # Sauvegarder dans le fichier
        with open("pathAnimation.txt", "w") as f:
            # PARTIE 1 : Liste simple
            f.write("=" * 60 + "\n")
            f.write("LISTE COMPLETE DES ANIMATIONS\n")
            f.write("=" * 60 + "\n\n")
            
            for i, behavior in enumerate(sorted(installed_behaviors), 1):
                f.write("{}. {}\n".format(i, behavior))
            
            # PARTIE 2 : Par catégorie
            f.write("\n\n" + "=" * 60 + "\n")
            f.write("ANIMATIONS PAR CATEGORIE\n")
            f.write("=" * 60 + "\n\n")
            
            for category in sorted(categories.keys()):
                f.write("\n[{}] ({} animations)\n".format(category, len(categories[category])))
                for behavior in sorted(categories[category]):
                    f.write("  - {}\n".format(behavior))
            
            # PARTIE 3 : Statistiques
            f.write("\n\n" + "=" * 60 + "\n")
            f.write("STATISTIQUES\n")
            f.write("=" * 60 + "\n")
            f.write("Total comportements : {}\n".format(len(installed_behaviors)))
            f.write("Total categories : {}\n".format(len(categories)))
            f.write("\nRepartition par categorie :\n")
            for category in sorted(categories.keys()):
                f.write("  - {} : {} animations\n".format(category, len(categories[category])))
        
        print("Fichier 'pathAnimation.txt' créé avec succès !")
        print("Total : {} animations dans {} catégories".format(
            len(installed_behaviors), len(categories)))
        print("\nConsultez le fichier pathAnimation.txt pour voir tous les détails.")
        
    except RuntimeError as e:
        print("Erreur de connexion :", e)
    except Exception as e:
        print("Erreur :", e)

if __name__ == "__main__":
    save_both_formats()