from dataclasses import dataclass


@dataclass
class EndingData:
    id: int
    ending: str

    def to_dict(self) -> dict:
        return {
            'id': self.id,
            'ending': self.ending
        }

    @classmethod
    def from_dict(cls, data_obj: dict):
        return cls(
            id=data_obj.get("id"),
            ending=data_obj.get("ending")
        )

    def __str__(self):
        return f'EndingData(id={self.id}, ending={self.ending})'
    
    def __repr__(self):
        return str(self)
