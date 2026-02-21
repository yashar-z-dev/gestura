# Score: 93/100
"""
NOTE: Part(1) is BaseModel, do validate (Use more CPU in hop path), but autocomplete is very nice.
NOTE: Part(2) is dataclasses, do convert data to object without validate, But it is very light.
NOTE: The input for this section comes from the OS, so we don't have to worry about validation.

__all__ = (
    _BaseGestureMouse, Axis_X, Axis_Y, GestureMouseValidator, GestureMouseAdapter, 
    GestureMouse, GestureMouseCondition, TEST_GestureMouse, Test_GestureMouseCondition
    )
"""

# NOTE: CPU 4% USE

from typing import Literal, Union, Annotated, overload, Iterable
from pydantic import BaseModel, Field, TypeAdapter, ConfigDict


# ========== Base models ==========
class _BaseGestureMouse(BaseModel):
    """
    Base Mouse Gesture

    NOTE: Valid Data: Union[Axis_X, Axis_Y].

    :param min_delta: Minimum move size(e.g. From a position of 200 pixels to 400 pixels is equal to a minimum delta of 200.)
    """

    model_config = ConfigDict(extra="forbid")

    min_delta: int


class Axis_X(_BaseGestureMouse):
    """
    :param axis: Axis of motion
    :param trend: up or down ("-" or "+")
    :param left: oprator `-`
    :param right: oprator `+`
    """
    axis: Literal["x"] = "x"
    trend: Literal["left", "right"]


class Axis_Y(_BaseGestureMouse):
    """
    :param axis: Axis of motion
    :param trend: up or down ("-" or "+")
    :param up: oprator `-`
    :param down: oprator `+`
    """
    axis: Literal["y"] = "y"
    trend: Literal["up", "down"]


# ===== Validators =====
GestureMouseValidator = Annotated[
    Union[Axis_X, Axis_Y],
    Field(discriminator="axis"),
]

GestureMouseAdapter = TypeAdapter(GestureMouseValidator)
GestureMouseListAdapter = TypeAdapter(list[GestureMouseValidator])


# ========== Container model ==========
class GestureMouse(BaseModel):
    """ 
    Model structure for Mouse Gesture.
    
    :param conditions: List of GestureMouseValidator for Mouse Actions (e.g. [{axis="x", trend="left", min_delta=444}, {axis="y", trend="up", min_delta=444}])
    """

    model_config = ConfigDict(extra="forbid")

    conditions: list[GestureMouseValidator] = Field(default_factory=list)


    @overload
    def add_condition(
        self,
        *,
        axis: Literal["x"],
        trend: Literal["left", "right"],
        min_delta: int,
    ) -> Axis_X: ...

    @overload
    def add_condition(
        self,
        *,
        axis: Literal["y"],
        trend: Literal["up", "down"],
        min_delta: int,
    ) -> Axis_Y: ...

    @overload
    def add_condition(
        self,
        data: Iterable[dict | GestureMouseValidator] | dict,
    ) -> list[GestureMouseValidator]: ...

    # -------- private API --------
    def _normalize_input(self, data: object) -> list[GestureMouseValidator]:
        """
        Normalize ANY supported input into list[GestureMouseValidator]
        """
        if isinstance(data, dict) and "conditions" in data:
            data = data["conditions"]

        if isinstance(data, list | tuple):
            return GestureMouseListAdapter.validate_python(data)

        # single item
        return [GestureMouseAdapter.validate_python(data)]

    # -------- implementation --------
    def add_condition(
        self,
        data: object = None,
        **kwargs: object,
    ):
        if kwargs:
            cond = GestureMouseAdapter.validate_python(kwargs)
            self.conditions.append(cond)
            return cond

        conds = self._normalize_input(data)
        self.conditions.extend(conds)
        return conds

    # -------- alternative API --------
    def add(self, cond: GestureMouseValidator) -> None:
        """Append one WITHOUT validation"""
        self.conditions.append(cond)

    def extend(self, conds: Iterable[GestureMouseValidator]) -> None:
        """Append many WITHOUT validation"""
        self.conditions.extend(conds)

    # -------- helpers --------
    def x(self) -> list[Axis_X]:
        """
        :return: filter Axis_X
        :rtype: list[GestureMouseValidator]
        """

        return [c for c in self.conditions if isinstance(c, Axis_X)]

    def y(self) -> list[Axis_Y]:
        """
        :return: filter Axis_Y
        :rtype: list[GestureMouseValidator]
        """

        return [c for c in self.conditions if isinstance(c, Axis_Y)]


# ===== SHORTCUT JSON Mouse =====
class GestureMouseCondition(GestureMouse):
    """
    Define mouse gestures for the conditions required to trigger the action.

    :param callback: The name of the method to be executed when the gesture is triggered (TODO: most update for support Callable and read plugins)
    """

    # callback: Callable[[], None] | str = "Unknown"
    callback: str = "Unknown"


# ===== Validators =====
GestureMouseConditionAdapter = TypeAdapter(list[GestureMouseCondition])

def Validator_GestureMouseCondition(data: list[dict]):
    """
    :param data: format GestureMouseCondition.

    :return: list[GestureMouseCondition]
    """

    return GestureMouseConditionAdapter.validate_python(data)







#############################################

# NOTE: CPU 1% USE

# from dataclasses import dataclass, field
# from typing import Literal, Optional, Callable, List, Union, Iterable


# # ===== Base classes =====
# @dataclass(slots=True)
# class _BaseGestureMouse:
#     """Base class for Mouse Gestures."""
#     min_delta: int


# @dataclass(slots=True)
# class Axis_X(_BaseGestureMouse):
#     axis: Literal["x"] = "x"
#     trend: Literal["left", "right"] = "left"


# @dataclass(slots=True)
# class Axis_Y(_BaseGestureMouse):
#     axis: Literal["y"] = "y"
#     trend: Literal["up", "down"] = "up"


# GestureMouseValidator = Union[Axis_X, Axis_Y]


# # ===== Container =====
# @dataclass(slots=True)
# class GestureMouse:
#     conditions: List[GestureMouseValidator] = field(default_factory=list)

#     # ---- add_condition with kwargs or iterable ----
#     def add_condition(self, data: object = None, **kwargs) -> Union[GestureMouseValidator, List[GestureMouseValidator], None]:
#         if kwargs:
#             axis = kwargs.get("axis")
#             if axis == "x":
#                 cond = Axis_X(**kwargs)
#             elif axis == "y":
#                 cond = Axis_Y(**kwargs)
#             else:
#                 return None  # skip invalid axis
#             self.conditions.append(cond)
#             return cond

#         if data is None:
#             return []

#         if isinstance(data, dict):
#             # dict with keys like {"axis":..., "trend":..., "min_delta":...}
#             axis = data.get("axis")
#             if axis == "x":
#                 cond = Axis_X(**data)
#             elif axis == "y":
#                 cond = Axis_Y(**data)
#             else:
#                 return []
#             self.conditions.append(cond)
#             return [cond]

#         if isinstance(data, Iterable):
#             result = []
#             for item in data:
#                 if isinstance(item, GestureMouseValidator):
#                     self.conditions.append(item)
#                     result.append(item)
#                 elif isinstance(item, dict):
#                     axis = item.get("axis")
#                     if axis == "x":
#                         cond = Axis_X(**item)
#                     elif axis == "y":
#                         cond = Axis_Y(**item)
#                     else:
#                         continue
#                     self.conditions.append(cond)
#                     result.append(cond)
#             return result

#         # single object
#         if isinstance(data, GestureMouseValidator):
#             self.conditions.append(data)
#             return [data]

#         return []

#     # ---- append without any checks ----
#     def add(self, cond: GestureMouseValidator) -> None:
#         self.conditions.append(cond)

#     def extend(self, conds: Iterable[GestureMouseValidator]) -> None:
#         self.conditions.extend(conds)

#     # ---- helpers ----
#     def x(self) -> List[Axis_X]:
#         return [c for c in self.conditions if isinstance(c, Axis_X)]

#     def y(self) -> List[Axis_Y]:
#         return [c for c in self.conditions if isinstance(c, Axis_Y)]


# # ===== Shortcut with callback =====
# @dataclass(slots=True)
# class GestureMouseCondition(GestureMouse):
#     callback: Callable[[], None] | str = "Unknown"

# def TEST_GestureMouse():
#     m = GestureMouse()

#     # add with kwargs (autocomplete)
#     m.add_condition(axis="x", trend="left", min_delta=10)
#     m.add_condition(axis="y", trend="up", min_delta=50)
#     m.add_condition(axis="y", trend="down", min_delta=37)

#     print("All conditions:", m.conditions)
#     print("X axis gestures:", m.x())
#     print("Y axis gestures:", m.y())

#     # add with dict
#     m.add_condition({"axis": "x", "trend": "right", "min_delta": 42})
#     print("After dict add:", m.conditions)

#     # add with iterable
#     batch = [
#         {"axis": "y", "trend": "up", "min_delta": 5},
#         Axis_X(trend="right", min_delta=7),
#         {"axis": "x", "trend": "left", "min_delta": 9}
#     ]
#     m.add_condition(batch)
#     print("After batch add:", m.conditions)


# def Test_GestureMouseCondition():
#     m = GestureMouseCondition()
#     m.add_condition(axis="x", trend="left", min_delta=100)
#     m.add_condition(axis="y", trend="down", min_delta=50)
#     m.callback = "test_callback"

#     print("GestureMouseCondition:", m)
#     for cond in m.conditions:
#         print(f"{cond.axis=}, {cond.trend=}, {cond.min_delta=}")
#     print("Callback:", m.callback)


# if __name__ == "__main__":
#     print("=== Testing GestureMouse ===")
#     TEST_GestureMouse()
#     print("\n=== Testing GestureMouseCondition ===")
#     Test_GestureMouseCondition()
