# ==== LAYER 4: Transactions ====
from app.models.deposit import Deposit
from app.models.withdrawal import Withdrawal
from app.models.transfer import Transfer
from app.models.interbank_transfer import InterbankTransfer

# ==== LAYER 4: Transactions ====
from app.routers import deposits, withdrawals, transfers, interbank_transfers

# ==== LAYER 4: Transactions ====
app.include_router(deposits.router)
app.include_router(withdrawals.router)
app.include_router(transfers.router)
app.include_router(interbank_transfers.router)

# ==== LAYER 4: Transactions ====
from app.models.deposit import Deposit
from app.models.withdrawal import Withdrawal
from app.models.transfer import Transfer
from app.models.interbank_transfer import InterbankTransfer