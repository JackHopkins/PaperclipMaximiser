
# place the steam engine and assembler at the origin
steam_engine = place_entity(Prototype.SteamEngine, position=Position(x=0, y=0))
assert steam_engine, "Failed to place steam engine"
assembler = place_entity_next_to(Prototype.AssemblingMachine1, reference_position=steam_engine.position,
                                      direction=RIGHT, spacing=10)
assert assembler, "Failed to place assembler"

# connect the steam engine to the assembler using electric poles
move_to(Position(x=5, y=5))
diagonal_assembler = place_entity(Prototype.AssemblingMachine1, position=Position(x=10, y=10))
poles_in_inventory = inspect_inventory()[Prototype.SmallElectricPole]
poles = connect_entities(steam_engine, assembler, connection_type=Prototype.SmallElectricPole)
poles2 = connect_entities(steam_engine, diagonal_assembler, connection_type=Prototype.SmallElectricPole)
assert poles and poles2, "Failed to connect steam engine to assembler using electric poles"

# make a final check on the inventory
current_poles_in_inventory = inspect_inventory()[Prototype.SmallElectricPole]
spent_poles = (poles_in_inventory - current_poles_in_inventory)
assert spent_poles == len(poles + poles2)