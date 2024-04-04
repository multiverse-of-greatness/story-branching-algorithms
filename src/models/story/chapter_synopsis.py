from dataclasses import dataclass


@dataclass
class ChapterSynopsis:
    chapter: int
    synopsis: str
    character_ids: list[int]
    scene_ids: list[int]

    def to_dict(self) -> dict:
        return {
            'chapter': self.chapter,
            'synopsis': self.synopsis,
            'character_ids': self.character_ids,
            'scene_ids': self.scene_ids
        }

    @classmethod
    def from_dict(cls, data_obj: dict):
        return cls(
            chapter=data_obj.get("chapter"),
            synopsis=data_obj.get("synopsis"),
            character_ids=data_obj.get("character_ids"),
            scene_ids=data_obj.get("scene_ids")
        )

    def __str__(self):
        return (f"ChapterSynopsis(chapter={self.chapter}, synopsis={self.synopsis}, "
                f"character_ids={self.character_ids}, scene_ids={self.scene_ids})")
    
    def __repr__(self):
        return str(self)
