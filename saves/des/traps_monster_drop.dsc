"ΝΦσβ"Ν   	drop_trap    ΊLuaQ         dlmapchunk           
      A@  @    A  @    A@  @             map        ...        .^.     
                                            2/home/dustin/bin/../dat/des/traps/monster_drop.des   D  LuaQ         dlmain           S      A@  @   Aΐ  @   A  @   A@ @   A @ ΐ A  @ @ΐ A ΐ @  A@ @    E FΐΓ  \ Z   ΐJ  I@DIΐDI@Eΐ  FΑ@  I    E FΐΓ ΐ \ Z   J  I@DI GI@GIF   @J  I@DIGIΐGIF   E  K@Θ Κΐ  ΙΐHΙ@IΙ  \ΐΙ 
 AHA  Κ@  ΐ
 Α    @  -          depth /       D:12-, Depths, Vaults, Elf, Spider, Snake, Zot        tags 
       allow_dup        extra        luniq_monster_drop        transparent        depth_weight *       D:12-, Depths, Vaults, Elf, Spider, Snake       Y@       Zot       4@       kfeat        ^ = pressure plate trap        you 
       in_branch 
       triggered         mons        generate_awake killer klown        msg M       With a honk a tiny klown kar falls from above, and Killer Klowns tumble out!        max        crawl        random_range       @       @       Snake 7       generate_awake black mamba / generate_awake mana viper %       A basket of snakes falls from above!        generate_awake redback &       A basket of spiders falls from above!        TriggerableFunction        new        func        callback.drop_trap_stepped 	       repeated        data        add_triggerer        DgnTriggerer        type        pressure_plate        lua_marker        ^     S                                                                                                            	   
                                                                                                                                                       trigger_data    R          tm G   R          2/home/dustin/bin/../dat/des/traps/monster_drop.des   '   