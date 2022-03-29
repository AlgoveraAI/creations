import gradio as gr
from ocean_lib.config import Config
from ocean_lib.models.compute_input import ComputeInput
from ocean_lib.ocean.ocean import Ocean
from ocean_lib.web3_internal.constants import ZERO_ADDRESS
from ocean_lib.web3_internal.currency import to_wei
from ocean_lib.web3_internal.wallet import Wallet
import matplotlib.pyplot as plt
import pickle
import time
import torch


config = Config('config.ini')
ocean = Ocean(config)

def compute(private_key):
    wallet = Wallet(ocean.web3, private_key, transaction_timeout=20, block_confirmations=config.block_confirmations)
    address = wallet.address

    DATA_ddo = ocean.assets.resolve("did:op:e772c8585ad9916eD677320078748DD1cA827BB2")
    data_token = ocean.get_data_token(DATA_ddo.data_token_address)
    token_address = data_token.address

    ALG_ddo = ocean.assets.resolve("did:op:d72296852f4196deF6093Ab2254a47B9e0266904")
    alg_token = ocean.get_data_token(ALG_ddo.data_token_address)

    DATA_did = DATA_ddo.did

    compute_service = DATA_ddo.get_service('compute')

    # order & pay for dataset
    dataset_order_requirements = ocean.assets.order(
        DATA_did, wallet.address, service_type=compute_service.type
    )
    DATA_order_tx_id = ocean.assets.pay_for_service(
            ocean.web3,
            dataset_order_requirements.amount,
            dataset_order_requirements.data_token_address,
            DATA_did,
            compute_service.index,
            ZERO_ADDRESS,
            wallet,
            dataset_order_requirements.computeAddress,
        )

    ALG_did = ALG_ddo.did

    algo_service = ALG_ddo.get_service('access')

    # order & pay for algo
    algo_order_requirements = ocean.assets.order(
        ALG_did, wallet.address, service_type=algo_service.type
    )
    ALG_order_tx_id = ocean.assets.pay_for_service(
            ocean.web3,
            algo_order_requirements.amount,
            algo_order_requirements.data_token_address,
            ALG_did,
            algo_service.index,
            ZERO_ADDRESS,
            wallet,
            algo_order_requirements.computeAddress,
    )

    compute_inputs = [ComputeInput(DATA_did, DATA_order_tx_id, compute_service.index)]

    job_id = ocean.compute.start(
        compute_inputs,
        wallet,
        algorithm_did=ALG_did,
        algorithm_tx_id=ALG_order_tx_id,
        algorithm_data_token=alg_token.address
    )

    status_dict = ocean.compute.status(DATA_did, job_id, wallet)
    while status_dict['statusText'] != 'Job finished':
        status_dict = ocean.compute.status(DATA_did, job_id, wallet)
        time.sleep(1)

    result = ocean.compute.result_file(DATA_did, job_id, 0, wallet)  # 0 index, means we retrieve the results from the first dataset index

    img = pickle.loads(result) 

    plt.figure(figsize=(5,5))
    plt.axis("off")
    plt.imshow(img)

    return address, plt

description = (
    "This demo serves a generative model from the Ocean marketplace. "
)

article = (
    "<p style='text-align: center'>"
    "<a href='https://market.oceanprotocol.com/' target='_blank'>Ocean marketplace</a> | "
    "<a href='https://oceanprotocol.com/technology/marketplaces#:~:text=Use%20Ocean%20Market%20to%20publish,Data%20has%20automatic%20price%20discovery.&text=It's%20a%20decentralized%20exchange%20(DEX)%2C%20tuned%20for%20data.' target='_blank'>More info</a> | "
    "<a href='https://www.algovera.ai' target='_blank'>Algovera</a>"
    "</p>"
)

interface = gr.Interface(
    compute,
    [
        gr.inputs.Textbox(label="Private Key"),
    ],
    [
        gr.outputs.Textbox(label="Public Key"),
        gr.outputs.Image(label="Output Image")
    ],
    title="Generative Model from the Ocean marketplace",
    description=description,
    article=article,
    theme="huggingface",
)

interface.launch()