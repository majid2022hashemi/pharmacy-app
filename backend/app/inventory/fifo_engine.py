# backend/app/inventory/fifo_engine.py

from dataclasses import dataclass
from typing import List
from app.repositories.medicine_batch_repository import MedicineBatchRepository


@dataclass
class BatchConsumption:
    batch_id: int
    quantity: int
    unit_price: float


class FIFOEngine:
    
    @staticmethod
    def consume_stock(
        db,
        medicine_id: int,
        quantity: int,
    ) -> List[BatchConsumption]:
        
        if quantity <= 0:
            raise ValueError(
                "Quantity must be greater than zero"
            )
        
        batches = (
            MedicineBatchRepository
            .get_available_batches_for_update(
                db=db,
                medicine_id=medicine_id,
            )
        )
        
        total_available = sum(
            batch.quantity_remaining
            for batch in batches
        )
        
        if total_available < quantity:
            raise ValueError(
                f"Insufficient stock. "
                f"Available={total_available}, "
                f"Requested={quantity}"
            )
        
        remaining = quantity
        
        consumptions: List[BatchConsumption] = []
        
        for batch in batches:
            
            if remaining == 0:
                break
            
            take = min(
                batch.quantity_remaining,
                remaining,
            )
            
            batch.quantity_remaining -= take
            
            consumptions.append(
                BatchConsumption(
                    batch_id=batch.id,
                    quantity=take,
                    unit_price=float(
                        batch.purchase_price
                    ),
                )
            )
            
            remaining -= take
        
        return consumptions