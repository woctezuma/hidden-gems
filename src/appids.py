# Objective: list appID of examples of "hidden gems"

# This is the appID of the game called "Contradiction".
APP_ID_CONTRADICTION = "373390"  # Contradiction - Spot The Liar!

# This is a set including appID of games which will serve as references of "hidden gems".
# Reference: http://www.neogaf.com/forum/showpost.php?p=241232835&postcount=5886
appid_hidden_gems_reference_set = {
    APP_ID_CONTRADICTION,  # Contradiction - Spot The Liar!
    "320090",  # This Starry Midnight We Make
    "363980",  # Forget Me Not: My Organic Garden
    "561740",  # MidBoss
    "333300",  # ADOM (Ancient Domains Of Mystery)
    "329970",  # KeeperRL
    "323220",  # Vagante
    "534290",  # Cursed Castilla (Maldita Castilla EX)
    "440880",  # The Count Lucanor
    "402040",  # The Guest
    "233980",  # UnEpic
}


def main() -> bool:
    print(appid_hidden_gems_reference_set)

    return True


if __name__ == "__main__":
    main()
