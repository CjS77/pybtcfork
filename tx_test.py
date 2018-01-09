from binascii import hexlify, unhexlify
from io import BytesIO
from unittest import TestCase

from ecc import PrivateKey, S256Point, Signature
from helper import (
    p2pkh_script,
    SIGHASH_ALL,
)
from script import Script
from tx import Tx, TxIn, TxOut, BCDTx, BTGTx, SBTCTx, BCHTx


class TxTest(TestCase):

    @classmethod
    def tearDownClass(cls):
        if TxIn.mainnet_socket is not None:
            TxIn.mainnet_socket.close()
            TxIn.mainnet_socket = None
        if TxIn.testnet_socket is not None:
            TxIn.testnet_socket.close()
            TxIn.testnet_socket = None
        if Tx.mainnet_socket is not None:
            Tx.mainnet_socket.close()
            Tx.mainnet_socket = None
        if Tx.testnet_socket is not None:
            Tx.testnet_socket.close()
            Tx.testnet_socket = None

    def test_parse_version(self):
        raw_tx = unhexlify('0100000001813f79011acb80925dfe69b3def355fe914bd1d96a3f5f71bf8303c6a989c7d1000000006b483045022100ed81ff192e75a3fd2304004dcadb746fa5e24c5031ccfcf21320b0277457c98f02207a986d955c6e0cb35d446a89d3f56100f4d7f67801c31967743a9c8e10615bed01210349fc4e631e3624a545de3f89f5d8684c7b8138bd94bdd531d2e213bf016b278afeffffff02a135ef01000000001976a914bc3b654dca7e56b04dca18f2566cdaf02e8d9ada88ac99c39800000000001976a9141c4bc762dd5423e332166702cb75f40df79fea1288ac19430600')
        stream = BytesIO(raw_tx)
        tx = Tx.parse(stream)
        self.assertEqual(tx.version, 1)

    def test_parse_inputs(self):
        raw_tx = unhexlify('0100000001813f79011acb80925dfe69b3def355fe914bd1d96a3f5f71bf8303c6a989c7d1000000006b483045022100ed81ff192e75a3fd2304004dcadb746fa5e24c5031ccfcf21320b0277457c98f02207a986d955c6e0cb35d446a89d3f56100f4d7f67801c31967743a9c8e10615bed01210349fc4e631e3624a545de3f89f5d8684c7b8138bd94bdd531d2e213bf016b278afeffffff02a135ef01000000001976a914bc3b654dca7e56b04dca18f2566cdaf02e8d9ada88ac99c39800000000001976a9141c4bc762dd5423e332166702cb75f40df79fea1288ac19430600')
        stream = BytesIO(raw_tx)
        tx = Tx.parse(stream)
        self.assertEqual(len(tx.tx_ins), 1)
        want = unhexlify('d1c789a9c60383bf715f3f6ad9d14b91fe55f3deb369fe5d9280cb1a01793f81')
        self.assertEqual(tx.tx_ins[0].prev_tx, want)
        self.assertEqual(tx.tx_ins[0].prev_index, 0)
        want = unhexlify('483045022100ed81ff192e75a3fd2304004dcadb746fa5e24c5031ccfcf21320b0277457c98f02207a986d955c6e0cb35d446a89d3f56100f4d7f67801c31967743a9c8e10615bed01210349fc4e631e3624a545de3f89f5d8684c7b8138bd94bdd531d2e213bf016b278a')
        self.assertEqual(tx.tx_ins[0].script_sig.serialize(), want)
        self.assertEqual(tx.tx_ins[0].sequence, 0xfffffffe)

    def test_parse_outputs(self):
        raw_tx = unhexlify('0100000001813f79011acb80925dfe69b3def355fe914bd1d96a3f5f71bf8303c6a989c7d1000000006b483045022100ed81ff192e75a3fd2304004dcadb746fa5e24c5031ccfcf21320b0277457c98f02207a986d955c6e0cb35d446a89d3f56100f4d7f67801c31967743a9c8e10615bed01210349fc4e631e3624a545de3f89f5d8684c7b8138bd94bdd531d2e213bf016b278afeffffff02a135ef01000000001976a914bc3b654dca7e56b04dca18f2566cdaf02e8d9ada88ac99c39800000000001976a9141c4bc762dd5423e332166702cb75f40df79fea1288ac19430600')
        stream = BytesIO(raw_tx)
        tx = Tx.parse(stream)
        self.assertEqual(len(tx.tx_outs), 2)
        want = 32454049
        self.assertEqual(tx.tx_outs[0].amount, want)
        want = unhexlify('76a914bc3b654dca7e56b04dca18f2566cdaf02e8d9ada88ac')
        self.assertEqual(tx.tx_outs[0].script_pubkey.serialize(), want)
        want = 10011545
        self.assertEqual(tx.tx_outs[1].amount, want)
        want = unhexlify('76a9141c4bc762dd5423e332166702cb75f40df79fea1288ac')
        self.assertEqual(tx.tx_outs[1].script_pubkey.serialize(), want)

    def test_parse_locktime(self):
        raw_tx = unhexlify('0100000001813f79011acb80925dfe69b3def355fe914bd1d96a3f5f71bf8303c6a989c7d1000000006b483045022100ed81ff192e75a3fd2304004dcadb746fa5e24c5031ccfcf21320b0277457c98f02207a986d955c6e0cb35d446a89d3f56100f4d7f67801c31967743a9c8e10615bed01210349fc4e631e3624a545de3f89f5d8684c7b8138bd94bdd531d2e213bf016b278afeffffff02a135ef01000000001976a914bc3b654dca7e56b04dca18f2566cdaf02e8d9ada88ac99c39800000000001976a9141c4bc762dd5423e332166702cb75f40df79fea1288ac19430600')
        stream = BytesIO(raw_tx)
        tx = Tx.parse(stream)
        self.assertEqual(tx.locktime, 410393)

    def test_der_signature(self):
        raw_tx = unhexlify('0100000001813f79011acb80925dfe69b3def355fe914bd1d96a3f5f71bf8303c6a989c7d1000000006b483045022100ed81ff192e75a3fd2304004dcadb746fa5e24c5031ccfcf21320b0277457c98f02207a986d955c6e0cb35d446a89d3f56100f4d7f67801c31967743a9c8e10615bed01210349fc4e631e3624a545de3f89f5d8684c7b8138bd94bdd531d2e213bf016b278afeffffff02a135ef01000000001976a914bc3b654dca7e56b04dca18f2566cdaf02e8d9ada88ac99c39800000000001976a9141c4bc762dd5423e332166702cb75f40df79fea1288ac19430600')
        stream = BytesIO(raw_tx)
        tx = Tx.parse(stream)
        want = b'3045022100ed81ff192e75a3fd2304004dcadb746fa5e24c5031ccfcf21320b0277457c98f02207a986d955c6e0cb35d446a89d3f56100f4d7f67801c31967743a9c8e10615bed'
        der, hash_type = tx.tx_ins[0].der_signature()
        self.assertEqual(hexlify(der), want)
        self.assertEqual(hash_type, SIGHASH_ALL)

    def test_sec_pubkey(self):
        raw_tx = unhexlify('0100000001813f79011acb80925dfe69b3def355fe914bd1d96a3f5f71bf8303c6a989c7d1000000006b483045022100ed81ff192e75a3fd2304004dcadb746fa5e24c5031ccfcf21320b0277457c98f02207a986d955c6e0cb35d446a89d3f56100f4d7f67801c31967743a9c8e10615bed01210349fc4e631e3624a545de3f89f5d8684c7b8138bd94bdd531d2e213bf016b278afeffffff02a135ef01000000001976a914bc3b654dca7e56b04dca18f2566cdaf02e8d9ada88ac99c39800000000001976a9141c4bc762dd5423e332166702cb75f40df79fea1288ac19430600')
        stream = BytesIO(raw_tx)
        tx = Tx.parse(stream)
        want = b'0349fc4e631e3624a545de3f89f5d8684c7b8138bd94bdd531d2e213bf016b278a'
        self.assertEqual(hexlify(tx.tx_ins[0].sec_pubkey()), want)

    def test_serialize(self):
        raw_tx = unhexlify('0100000001813f79011acb80925dfe69b3def355fe914bd1d96a3f5f71bf8303c6a989c7d1000000006b483045022100ed81ff192e75a3fd2304004dcadb746fa5e24c5031ccfcf21320b0277457c98f02207a986d955c6e0cb35d446a89d3f56100f4d7f67801c31967743a9c8e10615bed01210349fc4e631e3624a545de3f89f5d8684c7b8138bd94bdd531d2e213bf016b278afeffffff02a135ef01000000001976a914bc3b654dca7e56b04dca18f2566cdaf02e8d9ada88ac99c39800000000001976a9141c4bc762dd5423e332166702cb75f40df79fea1288ac19430600')
        stream = BytesIO(raw_tx)
        tx = Tx.parse(stream)
        self.assertEqual(tx.serialize(), raw_tx)

    def test_input_value(self):
        tx_hash = 'd1c789a9c60383bf715f3f6ad9d14b91fe55f3deb369fe5d9280cb1a01793f81'
        index = 0
        want = 42505594
        tx_in = TxIn(
            prev_tx=unhexlify(tx_hash),
            prev_index=index,
            script_sig=b'',
            sequence=0,
        )
        self.assertEqual(tx_in.value(), want)

    def test_input_pubkey(self):
        tx_hash = 'd1c789a9c60383bf715f3f6ad9d14b91fe55f3deb369fe5d9280cb1a01793f81'
        index = 0
        tx_in = TxIn(
            prev_tx=unhexlify(tx_hash),
            prev_index=index,
            script_sig=b'',
            sequence=0,
        )
        want = unhexlify('76a914a802fc56c704ce87c42d7c92eb75e7896bdc41ae88ac')
        self.assertEqual(tx_in.script_pubkey().serialize(), want)

    def test_fee(self):
        raw_tx = unhexlify('0100000001813f79011acb80925dfe69b3def355fe914bd1d96a3f5f71bf8303c6a989c7d1000000006b483045022100ed81ff192e75a3fd2304004dcadb746fa5e24c5031ccfcf21320b0277457c98f02207a986d955c6e0cb35d446a89d3f56100f4d7f67801c31967743a9c8e10615bed01210349fc4e631e3624a545de3f89f5d8684c7b8138bd94bdd531d2e213bf016b278afeffffff02a135ef01000000001976a914bc3b654dca7e56b04dca18f2566cdaf02e8d9ada88ac99c39800000000001976a9141c4bc762dd5423e332166702cb75f40df79fea1288ac19430600')
        stream = BytesIO(raw_tx)
        tx = Tx.parse(stream)
        self.assertEqual(tx.fee(), 40000)
        raw_tx = unhexlify('010000000456919960ac691763688d3d3bcea9ad6ecaf875df5339e148a1fc61c6ed7a069e010000006a47304402204585bcdef85e6b1c6af5c2669d4830ff86e42dd205c0e089bc2a821657e951c002201024a10366077f87d6bce1f7100ad8cfa8a064b39d4e8fe4ea13a7b71aa8180f012102f0da57e85eec2934a82a585ea337ce2f4998b50ae699dd79f5880e253dafafb7feffffffeb8f51f4038dc17e6313cf831d4f02281c2a468bde0fafd37f1bf882729e7fd3000000006a47304402207899531a52d59a6de200179928ca900254a36b8dff8bb75f5f5d71b1cdc26125022008b422690b8461cb52c3cc30330b23d574351872b7c361e9aae3649071c1a7160121035d5c93d9ac96881f19ba1f686f15f009ded7c62efe85a872e6a19b43c15a2937feffffff567bf40595119d1bb8a3037c356efd56170b64cbcc160fb028fa10704b45d775000000006a47304402204c7c7818424c7f7911da6cddc59655a70af1cb5eaf17c69dadbfc74ffa0b662f02207599e08bc8023693ad4e9527dc42c34210f7a7d1d1ddfc8492b654a11e7620a0012102158b46fbdff65d0172b7989aec8850aa0dae49abfb84c81ae6e5b251a58ace5cfeffffffd63a5e6c16e620f86f375925b21cabaf736c779f88fd04dcad51d26690f7f345010000006a47304402200633ea0d3314bea0d95b3cd8dadb2ef79ea8331ffe1e61f762c0f6daea0fabde022029f23b3e9c30f080446150b23852028751635dcee2be669c2a1686a4b5edf304012103ffd6f4a67e94aba353a00882e563ff2722eb4cff0ad6006e86ee20dfe7520d55feffffff0251430f00000000001976a914ab0c0b2e98b1ab6dbf67d4750b0a56244948a87988ac005a6202000000001976a9143c82d7df364eb6c75be8c80df2b3eda8db57397088ac46430600')
        stream = BytesIO(raw_tx)
        tx = Tx.parse(stream)
        self.assertEqual(tx.fee(), 140500)

    def test_sig_hash(self):
        raw_tx = unhexlify('0100000001813f79011acb80925dfe69b3def355fe914bd1d96a3f5f71bf8303c6a989c7d1000000006b483045022100ed81ff192e75a3fd2304004dcadb746fa5e24c5031ccfcf21320b0277457c98f02207a986d955c6e0cb35d446a89d3f56100f4d7f67801c31967743a9c8e10615bed01210349fc4e631e3624a545de3f89f5d8684c7b8138bd94bdd531d2e213bf016b278afeffffff02a135ef01000000001976a914bc3b654dca7e56b04dca18f2566cdaf02e8d9ada88ac99c39800000000001976a9141c4bc762dd5423e332166702cb75f40df79fea1288ac19430600')
        stream = BytesIO(raw_tx)
        tx = Tx.parse(stream)
        tx.testnet = True
        hash_type = SIGHASH_ALL
        want = int('27e0c5994dec7824e56dec6b2fcb342eb7cdb0d0957c2fce9882f715e85d81a6', 16)
        self.assertEqual(tx.sig_hash(0, hash_type), want)

    def test_verify_input1(self):
        raw_tx = unhexlify('0100000001813f79011acb80925dfe69b3def355fe914bd1d96a3f5f71bf8303c6a989c7d1000000006b483045022100ed81ff192e75a3fd2304004dcadb746fa5e24c5031ccfcf21320b0277457c98f02207a986d955c6e0cb35d446a89d3f56100f4d7f67801c31967743a9c8e10615bed01210349fc4e631e3624a545de3f89f5d8684c7b8138bd94bdd531d2e213bf016b278afeffffff02a135ef01000000001976a914bc3b654dca7e56b04dca18f2566cdaf02e8d9ada88ac99c39800000000001976a9141c4bc762dd5423e332166702cb75f40df79fea1288ac19430600')
        stream = BytesIO(raw_tx)
        tx = Tx.parse(stream)
        self.assertTrue(tx.verify_input(0))

    def test_verify_input2(self):
        raw_tx = unhexlify('0100000001868278ed6ddfb6c1ed3ad5f8181eb0c7a385aa0836f01d5e4789e6bd304d87221a000000db00483045022100dc92655fe37036f47756db8102e0d7d5e28b3beb83a8fef4f5dc0559bddfb94e02205a36d4e4e6c7fcd16658c50783e00c341609977aed3ad00937bf4ee942a8993701483045022100da6bee3c93766232079a01639d07fa869598749729ae323eab8eef53577d611b02207bef15429dcadce2121ea07f233115c6f09034c0be68db99980b9a6c5e75402201475221022626e955ea6ea6d98850c994f9107b036b1334f18ca8830bfff1295d21cfdb702103b287eaf122eea69030a0e9feed096bed8045c8b98bec453e1ffac7fbdbd4bb7152aeffffffff04d3b11400000000001976a914904a49878c0adfc3aa05de7afad2cc15f483a56a88ac7f400900000000001976a914418327e3f3dda4cf5b9089325a4b95abdfa0334088ac722c0c00000000001976a914ba35042cfe9fc66fd35ac2224eebdafd1028ad2788acdc4ace020000000017a91474d691da1574e6b3c192ecfb52cc8984ee7b6c568700000000')
        stream = BytesIO(raw_tx)
        tx = Tx.parse(stream)
        self.assertTrue(tx.verify_input(0))

    def test_sign_input(self):
        private_key = PrivateKey(secret=8675309)
        tx_ins = []
        prev_tx = unhexlify('0025bc3c0fa8b7eb55b9437fdbd016870d18e0df0ace7bc9864efc38414147c8')
        tx_ins.append(TxIn(
            prev_tx=prev_tx,
            prev_index=0,
            script_sig=b'',
            sequence=0xffffffff,
        ))
        tx_ins[0]._value = 110000000
        tx_ins[0]._script_pubkey = Script.parse(private_key.point.p2pkh_script())
        tx_outs = []
        h160 = Tx.get_address_data('mzx5YhAH9kNHtcN481u6WkjeHjYtVeKVh2')['h160']
        tx_outs.append(TxOut(amount=int(0.99*100000000), script_pubkey=p2pkh_script(h160)))
        h160 = Tx.get_address_data('mnrVtF8DWjMu839VW3rBfgYaAfKk8983Xf')['h160']
        tx_outs.append(TxOut(amount=int(0.1*100000000), script_pubkey=p2pkh_script(h160)))

        tx = Tx(
            version=1,
            tx_ins=tx_ins,
            tx_outs=tx_outs,
            locktime=0,
            testnet=True,
        )
        self.assertTrue(tx.sign_input(0, private_key, SIGHASH_ALL))

    def test_is_coinbase(self):
        raw_tx = unhexlify('01000000010000000000000000000000000000000000000000000000000000000000000000ffffffff5e03d71b07254d696e656420627920416e74506f6f6c20626a31312f4542312f4144362f43205914293101fabe6d6d678e2c8c34afc36896e7d9402824ed38e856676ee94bfdb0c6c4bcd8b2e5666a0400000000000000c7270000a5e00e00ffffffff01faf20b58000000001976a914338c84849423992471bffb1a54a8d9b1d69dc28a88ac00000000')
        stream = BytesIO(raw_tx)
        tx = Tx.parse(stream)
        self.assertTrue(tx.is_coinbase())

    def test_coinbase_height(self):
        raw_tx = unhexlify('01000000010000000000000000000000000000000000000000000000000000000000000000ffffffff5e03d71b07254d696e656420627920416e74506f6f6c20626a31312f4542312f4144362f43205914293101fabe6d6d678e2c8c34afc36896e7d9402824ed38e856676ee94bfdb0c6c4bcd8b2e5666a0400000000000000c7270000a5e00e00ffffffff01faf20b58000000001976a914338c84849423992471bffb1a54a8d9b1d69dc28a88ac00000000')
        stream = BytesIO(raw_tx)
        tx = Tx.parse(stream)
        self.assertEqual(tx.coinbase_height(), 465879)
        raw_tx = unhexlify('0100000001813f79011acb80925dfe69b3def355fe914bd1d96a3f5f71bf8303c6a989c7d1000000006b483045022100ed81ff192e75a3fd2304004dcadb746fa5e24c5031ccfcf21320b0277457c98f02207a986d955c6e0cb35d446a89d3f56100f4d7f67801c31967743a9c8e10615bed01210349fc4e631e3624a545de3f89f5d8684c7b8138bd94bdd531d2e213bf016b278afeffffff02a135ef01000000001976a914bc3b654dca7e56b04dca18f2566cdaf02e8d9ada88ac99c39800000000001976a9141c4bc762dd5423e332166702cb75f40df79fea1288ac19430600')
        stream = BytesIO(raw_tx)
        tx = Tx.parse(stream)
        self.assertIsNone(tx.coinbase_height())

    def test_sig_hash_bip143(self):
        raw_tx = unhexlify('0100000001fd5145175fafdee6d20ac376e376cf26d933848ba5aa177d0d163a462fb3f183010000006b483045022100f49a17e80098bc057e319b890bdc42fe7224e7f6beb69a650102f802239be154022069742f504fdd52906c14d0d18ff0808e01146813775602163ec10d419270c1c541210223f1c80f382f086e2af7ad9d05227d94b6cf292596b9853f04a91194048f9048ffffffff0236820100000000001976a914dc10e999a5f18eb510feec09206d1812fa24a9c288ac5c058049000000001976a91421704f258089af191df1a4abed2b48ec11d6063e88ac00000000')
        stream = BytesIO(raw_tx)
        tx = BCHTx.parse(stream)
        tx_in = tx.tx_ins[0]
        raw_tx2 = unhexlify('010000000185037eb5531900f2f450e55cd950c509310229c0444e318a8811eecfa3b5c183010000006b483045022100f4a6e308ff7846bd19d394ec1b7263e051f2a60e6819feb006cdb9047bdd21a502206d969dfb5dfee3e53ed1a79b441d1cc2b7b8fe945ac7507c3b5e180565fbaead4121037765d8921f9559a6f03d620a1687a57e5b4ecb9efa5b41fc44555da0a376f81affffffff021ffc6c00000000001976a914fe1f6bea216c790c30d07f52966850268a3f90a788acfc8b8149000000001976a9142563b8536a228ec866e1c1084044a7730e53758888ac00000000')
        stream2 = BytesIO(raw_tx2)
        tx2 = BCHTx.parse(stream2)
        tx_in._value = tx2.tx_outs[1].amount
        tx_in._script_pubkey = tx2.tx_outs[1].script_pubkey
        der, hash_type = tx_in.der_signature()
        sec = tx_in.sec_pubkey()
        sig = Signature.parse(der)
        point = S256Point.parse(sec)
        z = tx.sig_hash_bip143(0, hash_type)
        self.assertTrue(point.verify(z, sig))
        self.assertTrue(tx.verify_input(0))
        self.assertTrue(tx.verify())

        raw_tx = unhexlify('01000000066f267f335a54abf404c66a7a6e9ed3d77566a09ce11632f57029a677f42c6095000000006b483045022100fb0b16699c9b0984345c7860e208c04694aaa5117c8306082cfafc58b53e489a02203cd53408f1f8c8ff29701a9d1f6960b2dc5e1039f0eea949c5a886ac367e1e38412102fdcae0e5a55b20c8d3cbdf451d39f6d47daa50f884ed0ffcf0ae0adfeec4abb9ffffffff4ceb6a2894b19b96fedd543750bf7307805a2f6ca189c8c42d1abbe2930235fa000000006a4730440220794c269d519b567aa694de6dcde1d09dffa30b69dc18a619ce9ea65f239899150220156394f70f405c0710851490b9f21dc8a23931fbdc8a70ea51f73e9b00274a5c412103b708cd0b3329cff03611b0155384d1d4f40cb3aa30f82d8f4a34da044c868058ffffffff15053ac5123a25e0adf0ed998dfb710fff827861ac1a4c6601be8034179350ab000000006a473044022020e7b448318fa44b977d557b639aaf3a9666cf6d8dd446bd7812e752ddfcd1d302207159d22c2e379b77b0514b8e0767d0e9fff7063a659c268d605be436f65703884121031a97eb1664ceffa32988f7ea7c6726d681f1385b9765be1a40d6083fba4e6c69ffffffff2e1fb2ad94461104b147ffe95d0534eb98495c45831547b70eae652ac6cf52d0000000006b483045022100b0ce5496d51673f82430eee24c57f7f2f2631e5b9b32c78bbd79e1cbf3f6297b02201c807ecfa86c1c493e83f1235a19e4426da651e8f76c2f4b41ceebf1222a9291412102e4aa3631fd0b4a877c7c0a040b8211636f743c392ce17e6f266beb1b62490af9ffffffff311368bcf1bac2ae2e906bd7e84e9b45da861a63154ae5c3d69840f65486ba86000000006b483045022100d5f63c5284604eefb942fa9710f8d5b5bccf431e63c496237a0c41eb5c6debf102202bda17f3b7406b9c41f44c7377261413cfa144489a70a40e9e9126b3e7f2fc734121032e413587a71814365b7912eac3a052d8ac0c5f2351d3d84863a02bafefd41f19ffffffff2e9e219c5a68079891a8d2b00bfcf3772fa605997773c2c516bb5ac99aa8ee06000000006a47304402207b6e0d96d0ce538fb54fcb1731a35632b6e40efde834ce45ee22f0c0f5baa886022009327de37e3fb657af29161d265db558869c09e295e84ddb2f686a492db0015a41210389c44f336f7c8cc3096f8f40bc5bdbffea24da9e26649dbe6b862d7d369698d0ffffffff0102b84f05000000001976a9145c52250125494685f133df34f47fb88799b2903588ac00000000')
        stream = BytesIO(raw_tx)
        tx = BCHTx.parse(stream)
        inputs = (
            ('18Lk6CB2WSpc4BVbxWhZrxLaYaJA2XVtyU', 24285000),
            ('13xY6E2tnBC5eGFCkayAUdVVcuGkFPoebJ', 824730),
            ('1BjFmsA4StiDa9xjAwahFXNpzR6SfXxBFD', 7583000),
            ('1Nn5QirD9iFT5kSF35XN8E3SX3SJM1daPL', 13150000),
            ('1HE8AdXHkP2bbnKmgENET4iyCHncP7rd7G', 32850000),
            ('1J3BgNjoqeR5JhHzC2rgorzBXTmdbmYcau', 10422900),
        )
        for i, data in enumerate(inputs):
            addr, value = data
            tx_in = tx.tx_ins[i]
            i += 1
            h160 = Tx.get_address_data(addr)['h160']
            tx_in._value = value
            tx_in._script_pubkey = Script.parse(p2pkh_script(h160))
        self.assertTrue(tx.verify())

    def test_bch(self):
        raw = unhexlify('01000000021128db2baee531447170d0916a553b07e8912a1c47e4e174afc7bfdf4afd3185010000008a4730440220211497a5609bcdeba19552e54a96b63f153656ecc5ba997ca8174a8102b4d8c602206a079685c36b46902ba366e112ba17b44e79dc8cb9b3b4792848c4f2f97192ae41410456e1306c1068ff31f1e8dbdd0b976092b1b4903b1a8ee3fe878508fa7f584d399b3a0a48c4215cded444257ce358b04720c62c73d5a8c0bb4ad261096baaaec4ffffffffedc5aa7918bd8beb801277177b3b7d15924682358e6342570be84f91e6d11835010000008a47304402203b0ee7aedaa5237325caee0433eeaba2ce2aff53d5c09c91bc2a79c51500f0b702201ecfd381d027a0d08b2409691bc73c16e626cbcd3c80a9980fa1e41b7a11cb5041410456e1306c1068ff31f1e8dbdd0b976092b1b4903b1a8ee3fe878508fa7f584d399b3a0a48c4215cded444257ce358b04720c62c73d5a8c0bb4ad261096baaaec4ffffffff01ac3ae60e000000001976a91441e904a482e61766cec490a8a5f3fbcf6bffdb2a88ac00000000')
        stream = BytesIO(raw)
        tx = BCHTx.parse(stream)
        self.assertTrue(tx.verify())

    def test_btg(self):
        raw = unhexlify('0200000002618c8a9c486a961e57e99c8a249cd43937f4447083a3c9589cc30eebb38e0d8d010000006a473044022075173f771f997652e94c461a22147c1154336fb498cfb2cc4a5af5d0b94f43960220322a22f4290a580e3f0953cff7ba548c63d0829936413fc805a802bb005881014121034a66bef852adc6fa774d95a7ebef5a2b18e3b61d05e23130b9a4ad6fffa536bdfeffffff8afa4e2c895facf0354e66910cf6ed02e8549eaad8926688dedb754781e118b2010000006a473044022025575c1912ae89a29a639fca6ac3d72423214dbff62afd7a48a358464585da0d022068706419a61e60a571c084797177856f514a9ecd8d8df2f2e113c5daa4e560f041210259316ac5f9f5fecb6597929de0cb05739432b067b79444a57adbf9e413fc61defeffffff021f7a1b1d000000001976a914dd23a9af489c2b1e08a13122aac1a06752df8ed188ac7af11400000000001976a914bd31883c773888a0f99e16deeff118ff0ec15d0888ac7dbf0700')
        stream = BytesIO(raw)
        tx = BTGTx.parse(stream)
        tx.tx_ins[0]._value = 488779958
        h160 = BTGTx.get_address_data('GWmfLaQ7ZKmUX7rmW63u63b9ghbuwr9yN1')['h160']
        tx.tx_ins[0]._script_pubkey = Script.parse(p2pkh_script(h160))
        tx.tx_ins[1]._value = 969979
        h160 = BTGTx.get_address_data('GgvZtZ8aV1UhTgLzzRbXVLrwwVoJL9WywW')['h160']
        tx.tx_ins[1]._script_pubkey = Script.parse(p2pkh_script(h160))
        self.assertTrue(tx.verify())

    def test_bcd(self):
        raw = unhexlify('0c00000025b6923ff3cb4264408ed5d5cca3cc41c7586820c95aeec24503d5a11418dd2501d0b96dd7ff4e3de5113ca48cefcbb4083541154c75e51a2e7b09879301a71cc5000000006a47304402201e10a7a5d03235236475feede87c57a38a79ab3399aafe90fcb9c47de525603b0220547fd8897c0e9d318dbe6c350c784eeb31b3cb18fbf550516fcc0168c22810e5012103e97b79d9aa924bfcea2915235ebc5b4cc7db5414e63ccb61ed2d197e29cb9fdbffffffff0280cb7831000000001976a91449664b451210fc8b3c055ce5606f0d8199ceae6788ac5a434600000000001976a9148868e1942ff8445f2e3791d9fa1dc881b8aec08c88ac00000000')
        stream = BytesIO(raw)
        tx = BCDTx.parse(stream)
        tx.tx_ins[0]._value = 834614762
        h160 = BCDTx.get_address_data('1MtE3mjo4AByFJSB8bAuVUHeqb21brLKJ5')['h160']
        tx.tx_ins[0]._script_pubkey = Script.parse(p2pkh_script(h160))
        self.assertTrue(tx.verify())

    def test_sbtc(self):
        raw = unhexlify('0100000002a81e0df5218289cc4ee761a1747b494990cc1f5b2dc84f0542ad6f28f69d5f4c040000006b483045022100aaf4a05870a9a8ca79a612600936d27bbfce97ebf4e2fe4d311e40c4b78ca6550220175ecff50679023ffce58019ee711784229b8c738b85093d34b4ccc72592087341210313910dbdf4ecfc35f6193b8f6484ab554587f6c7e5e376351e0978e7433d8c80ffffffff17a8282d91fccc03f7d422f5b124427c09c391aca3743cc1e04b7afbe8e282b9010000006b483045022100ef1c6716e19cf7de6eea6cb6468ce7efb2480d72795dc2066d7b1ea823830a6102204cbcdc56e420d9a88a650c126375815443636a0d628096b1439814445156bb0a41210313910dbdf4ecfc35f6193b8f6484ab554587f6c7e5e376351e0978e7433d8c80ffffffff01a05d5804000000001976a9144c3496d9f64847b45318baa5afd6b515c76013cf88ac00000000')
        stream = BytesIO(raw)
        tx = SBTCTx.parse(stream)
        tx.tx_ins[0]._value = 67700000
        h160 = SBTCTx.get_address_data('14fR5g6ypHFx3F9mJwiHaHXkMs5YjS4fJZ')['h160']
        tx.tx_ins[0]._script_pubkey = Script.parse(p2pkh_script(h160))
        tx.tx_ins[1]._value = 5300000
        tx.tx_ins[0]._script_pubkey = Script.parse(p2pkh_script(h160))
        self.assertTrue(tx.verify())

    def test_fetch_address_utxos(self):
        addr = 'mgzCpjQxLVmw89FRrxrZqpzfE33HRAjaSU'
        utxos = Tx.fetch_address_utxos(addr)
        total = 0
        for prev_tx, prev_index, value in utxos:
            total += value
        self.assertTrue(total > 0)
