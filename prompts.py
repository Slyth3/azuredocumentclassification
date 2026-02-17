def get_prompts ():

    document_types = """Medical Aid/ Medical Scheme Certificate, Employee Tax Certificate, Retirement Annuity Certificate, Investment Income Certificate,
                     Medical Expenses, Travel Log Book, Other"""


    user_prompt = f"""Analyze the following text and classify the document type(s)"""

    system_prompt = f"""You are a document classification agent for the South African Revenue Service. 
    Your task is to analyze the provided text and classify it into one or more document types. 
    Valid types are strictly limited to: {document_types}. 
    If 'Other' is used, you must specify the exact type in plain text (e.g., 'Proof of donations', 'travel logbook', 'Bank Statement', 'Invoice' etc). 
    You must respond ONLY in valid JSON with the following structure:
    {{
    "Result": "<comma-separated list of identified types>",
    "Confidence": <confidence score between 0.0 and 1.0>,
    "Explanation": "<short explanation of why these types were chosen>"
    }}
    The Confidence score should reflect how certain you are about the classification:
    - 0.9-1.0: Very high confidence, clear and unambiguous document
    - 0.7-0.89: High confidence, strong indicators present
    - 0.5-0.69: Moderate confidence, some ambiguity
    - Below 0.5: Low confidence, significant uncertainty
    SAFETY AND RELIABILITY RULES:
    - Avoid ungrounded content.
    - Do not include any text outside of this JSON object. 
    - Do not infer, guess, or assume document types.
    - If more than one category type is identified, separate them with commas.
    - Ensure the JSON is properly formatted.
    - If the document type cannot be confidently determined, return "Other" and explain why.
    """

    example_response = """
    {"Result": "Employee Tax Certificate",
    "Confidence": 0.95,
    "Explanation": "The document is explicitly labeled as an Employee Income Tax Certificate IRP5/IT3(a) and contains employee income, tax references, and employer details."
    }"""
    example_text = """SARS South African Revenue Service\nTransaction Year (CCYY)\n2023\nYear of Assessment (CCYY)\n2023\nPeriod of Reconciliation (CCYYMM)\n202302\nEmployee Income Tax Certifcate\nIRP5/IT3(a)\nType of Certificate\nIRP5\nNature of Person\nA\nEmployee Information\nIRPINF01\nEmployee Number\nPS0052\nSurname / Trading Name\nWhitehead\nFirst Two Names\nSarah Jade\nInitials\nSJ\nDate of Birth (CCYYMMDD)\n19870528\nID No.\n8705280046083\nIncome Tax Ref. No.\n2312807148\nPassport/ Permit No.\nPassport Country/ Country of Origin (eg South Africa = ZAF)\nHome Tel No.\n072 391 9200\nBus. Tel No.\nFax No.\nCell No.\nContact Email\nEmployee Address Details - Residential\nUnit No.\nComplex (if applicable)\nStreet No.\n35\nStreet/Name of Farm\nPlatan Ave\nSuburb/District\nFlamwood\nCity/Town\nKlerksdorp\nPostal Code\n2576\nCountry Code\nZA\nEmployee Address Details - Postal\nPostal Address Structure\nPOSTAL ADDRESS SAME AS RESIDENTIAL ADDRESS\nCare of Address Y X indicator :unselected: N :selected:\nCare of Intermediary\nCertificate No.\n722079222220230200000001065513 :unselected:\nCertificate Number :00722079222220230200000001065513 ITRQWA01\nBank Account Details :unselected: Mark here with an "X" if not paid electronically or if foreign bank account\nAccount Holder Name\nSJ Whitehead\nBank Name\nFIRST NATIONAL BANK\nBranch No.\n250655\nBranch Name\nAccount No.\n62366662239\nAccount Type\nCurrent/Cheques\nAccount Holder Relationship\nOwn\nEmployer Information\nPAYE Ref No.\n7220792222\nSDL Ref No.\nL220792222\nUIF Ref No.\nU220792222\nTrading or Other Name\nPayProp Services\nEmployee Physical Work Address\nUnit No.\nComplex(if applicable)\nStreet No.\n38\nStreet/Name of Farm\nDorp Street\nSuburb/District\nCity/Town\nStellenbosch\nPostal Code\n7600\nCountry Code\nZA\nPay Periods\nETI Employment Date (CCYYMMDD)\nCertificate Tax Period Start Date (CCYYMMDD)\n20220301\nCertificate Tax Period End Date (CCYYMMDD)\n20220930\nPeriods in Year of Assessment\n12.0000\nNo. of Periods Worked\n7.0000\nVoluntary Over Deduction\nY :unselected: N :selected: X\nFixed rate Taxation Indicator\nY :unselected: N :selected: X\nDirectives\nDirective No.\nDirective No.\nDirective No.\nDirective No.\nDirective No.\nCCYYMMDD\nCCYYMMDD\nCCYYMMDD\nCCYYMMDD\nCCYYMMDD\nSource Code\nAmount R\nSource Code\nAmount R\nSource Code\nAmount R\nSource Code\nAmount R\nSource Code\nAmount"""
    
    return user_prompt, system_prompt, example_text, example_response