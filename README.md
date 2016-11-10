<b>Simple symmetric encryption script to be used with the Hexchat IRC client.</b>

The goal with this experiment/project was to as simple and slim as possible with only one script-file add symmetric encryption between two or more IRC users sharing the same password file. To keep it simple without the need of installing external python libraries the script uses the openssl-command-line-client (https://wiki.openssl.org/index.php/Manual:Enc(1)) for encryption and decryption using 256 bit AES-CBC encryption. 

