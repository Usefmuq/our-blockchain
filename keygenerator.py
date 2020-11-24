import ecdsa

sk = ecdsa.SigningKey.generate(curve=ecdsa.SECP256k1)  # this is your sign (private key)
private_key = sk.to_string().hex()  # convert your private key to hex
vk = sk.get_verifying_key()  # this is your verification key (public key)
public_key = vk.to_string().hex()
# we are going to encode the public key to make it shorter
# public_key = base64.b64encode(bytes.fromhex(public_key))
print("Private key:", private_key)
print("Public key:", public_key)
sk.sign

# ----------------------------------here is to try to understand how it work----------------------------------
# private_key = "eb67c68d70d1677f1d37786b12e1fd58ea9574955fdc88adeedd8dc132a88d0e"
# public_key = "8TYDy1JRIy+c1vwxgiHlg+XIVNZAKopxdAa41WCJ/5C95lJERnKKm9/cVWwdFmCO5u2El2/m8WizrnVg4z2w3w=="
# message = "HEllo"
# bmessage = message.encode()
# sk = ecdsa.SigningKey.from_string(bytes.fromhex(private_key), curve=ecdsa.SECP256k1)
# signature = base64.b64encode(sk.sign(bmessage))
# print(signature)
# print(message)

# public_key = (base64.b64decode(public_key)).hex()
# signature = base64.b64decode(signature)
# vk = ecdsa.VerifyingKey.from_string(bytes.fromhex(public_key), curve=ecdsa.SECP256k1)
# try:
#     print("work")
#     print(vk.verify(signature, message.encode()))
# except:
#     print("X work")


# ----------------------------------here is the old code----------------------------------
# from cryptography.hazmat.backends import default_backend
# from cryptography.hazmat.primitives import serialization, hashes
# from cryptography.hazmat.primitives.asymmetric import ec

# private_key = ec.generate_private_key(ec.SECP256K1(), default_backend())
# serialized_private = private_key.private_bytes(
#     encoding=serialization.Encoding.PEM,
#     format=serialization.PrivateFormat.PKCS8,
#     encryption_algorithm=serialization.BestAvailableEncryption(
#         b"testpassword"),
# )
# # print(serialized_private)

# public_key = private_key.public_key()
# serialized_public = public_key.public_bytes(
#     encoding=serialization.Encoding.PEM,
#     format=serialization.PublicFormat.SubjectPublicKeyInfo,
# )
# # print(serialized_public)
