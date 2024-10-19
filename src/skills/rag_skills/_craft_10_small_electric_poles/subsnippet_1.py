def harvest_resources(resource: Resource, amount: int) -> None:
    """
    Harvest the specified amount of a given resource.
    
    :param resource: The resource to harvest (Resource enum)
    :param amount: The amount of resource to harvest
    :return: None
    """
    # [PLANNING]
    # 1. Find the nearest patch of the specified resource
    # 2. Move to the resource patch
    # 3. Harvest the resource
    # 4. Verify that we've harvested the correct amount
    # 5. Print the current inventory for logging purposes
    # [END OF PLANNING]

    # Step 1: Find the nearest patch of the specified resource
    resource_position = nearest(resource)
    assert resource_position, f"No {resource.name} found nearby"
    print(f"Found {resource.name} at position: {resource_position}")

    # Step 2: Move to the resource patch
    move_to(resource_position)
    print(f"Moved to {resource.name} patch at {resource_position}")

    # Step 3: Harvest the resource
    # We'll harvest a bit more than needed to account for any inefficiencies
    harvest_amount = int(amount * 1.2)
    harvested = harvest_resource(resource_position, harvest_amount)
    print(f"Attempted to harvest {harvest_amount} {resource.name}")

    # Step 4: Verify that we've harvested the correct amount
    inventory = inspect_inventory()
    actual_amount = inventory.get(resource, 0)
    assert actual_amount >= amount, f"Failed to harvest enough {resource.name}. Expected at least {amount}, but got {actual_amount}"

    # Step 5: Print the current inventory for logging purposes
    print(f"Successfully harvested {actual_amount} {resource.name}")
    print(f"Current inventory: {inventory}")

    # If we harvested more than needed, we can optionally inform the user
    if actual_amount > amount:
        print(f"Note: Harvested {actual_amount - amount} extra {resource.name}")