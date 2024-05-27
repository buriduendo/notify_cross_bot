from sqlalchemy import String, BigInteger, Boolean, Date, Time, ForeignKey
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship
from sqlalchemy.ext.asyncio import AsyncAttrs, async_sessionmaker, create_async_engine, AsyncSession


from config import ENGINE, ECHO

engine = create_async_engine(url=ENGINE, echo=ECHO)

async_session = async_sessionmaker(engine, class_=AsyncSession)


class Base(AsyncAttrs, DeclarativeBase):
    pass


class Worker(Base):
    __tablename__ = 'worker'

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    firstName: Mapped[str] = mapped_column(String(50), nullable=False)
    lastName: Mapped[str] = mapped_column(String(50), nullable=False)
    email: Mapped[str] = mapped_column(String(100), nullable=False)
    password: Mapped[str] = mapped_column(String(50), nullable=True)
    tgID = mapped_column(BigInteger, nullable=True)
    isAdmin: Mapped[bool] = mapped_column(Boolean, default=False)

    materials = relationship("Material", back_populates="worker")


class Material(Base):
    __tablename__ = 'material'

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    lectureName: Mapped[str] = mapped_column(String(50))
    eventId: Mapped[int] = mapped_column(ForeignKey('event.id'), nullable=True)
    workerId: Mapped[int] = mapped_column(ForeignKey('worker.id'), nullable=False)

    event = relationship("Event", back_populates="materials")
    worker = relationship("Worker", back_populates="materials")

class Event(Base):
    __tablename__ = 'event'

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    eventType: Mapped[str] = mapped_column(String(20))
    dateOfEvent: Mapped[Date] = mapped_column(Date)
    timeOfEvent: Mapped[Date] = mapped_column(Time)
    eventLink: Mapped[str] = mapped_column(String(500), nullable=False)
    feedBackLink: Mapped[str] = mapped_column(String(500), nullable=True)
    videoLink: Mapped[str] = mapped_column(String(500), nullable=True)

    materials = relationship("Material", back_populates="event")

class Notification(Base):
    __tablename__ = 'notification'

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    notificationType: Mapped[str] = mapped_column(String(20), nullable=False)
    link: Mapped[str] = mapped_column(String(500), nullable=True)
    notificationText: Mapped[str] = mapped_column(String(1000), nullable=False)


async def async_main():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)