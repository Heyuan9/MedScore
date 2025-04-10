

def process_claim(claims):
    """
    Process the claim to remove any unwanted characters and split it into individual claims.
    
    Args:
        claims (list): A list of claims to be processed.
        
    Returns:
        list: A list of processed claims.
    """

    # drop - in front of the claim
    claims = [claim.strip('-').strip() for claim in claims]

    # remove 'no verifiable claim' from the claims
    claims = [claim for claim in claims if 'no verifiable claim' not in claim.lower()]
    
    return claims