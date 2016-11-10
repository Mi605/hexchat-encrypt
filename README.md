<b>Simple symmetric encryption script to be used with the Hexchat IRC client.</b>

The goal with this experiment/project was to as simple and slim as possible with only one file add symmetric encryption between two or more IRC users. To keep it simple without the need of installing external python libraries the script uses the openssl-command-line-client (https://wiki.openssl.org/index.php/Manual:Enc(1)) for encryption and decryption using 256 bit AES-CBC encryption. 

In the script change:
</br>
<i>PASSFILE = "/path/to/password/file"</i>
