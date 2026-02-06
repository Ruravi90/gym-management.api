import bcrypt

# Create the __about__ module attribute that passlib expects
if not hasattr(bcrypt, '__about__'):
    class About:
        __version__ = getattr(bcrypt, '__version__', '4.0.1')
    bcrypt.__about__ = About()