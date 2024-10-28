from ..utils.db import db, TimestampMixin


class HoneycombDependency(db.Model):
    honeycomb_id = db.Column('honeycomb_id', db.Integer(), db.ForeignKey('honeycomb.id'), primary_key=True, nullable=False)
    honeycomb_dependency_id = db.Column(
        'honeycomb_dependency_id', db.Integer(), db.ForeignKey('honeycomb.id'), primary_key=True, nullable=False
    )


class Honeycomb(TimestampMixin, db.Model):
    id = db.Column(db.Integer(), primary_key=True)
    name = db.Column(db.String(256), nullable=False)
    description = db.Column(db.Text(), nullable=False)
    version = db.Column(db.Integer(), nullable=False)
    code = db.Column(db.JSON(), nullable=False)

    # honeycombs can depend on other honeycombs
    honeycomb_dependencies = db.relationship(
        'Honeycomb', 
        secondary='honeycomb_dependency', 
        primaryjoin=id==HoneycombDependency.honeycomb_id,
        secondaryjoin=id==HoneycombDependency.honeycomb_dependency_id
    )

    # TODO: fields to be added in the future
    # Add supported language and version (Python 3.8 supported code won’t necessarily work on Python 3.7)
    # Labels - frontend, backend, scraping, react, python, etc...
    # Category - we may want to wait with this and then the category can be a hierarchical representation of labels

    def __init__(
        self, name, description, version, code, honeycomb_dependencies
    ):
        self.name = name
        self.description = description
        self.version = version
        self.code = code
        self.honeycomb_dependencies = honeycomb_dependencies

    def __repr__(self):
        return f'<Honeycomb {self.id}>'

    def get_dependencies(self, recursive=True):
        """
        Returns all the dependencies of a honeycomb as a tuple of honeycomb dependencies and package dependencies.

        Args:
            recursive - if set to True, it'll return the dependencies of the dependencies as well (throughout all levels)
        """
        # take the honeycomb + package dependencies for the current honeycomb
        honeycomb_dependencies = set(self.honeycomb_dependencies)

        # if needed, loop through the dependencies and add their dependencies to the set
        if recursive:
            for dependency in self.honeycomb_dependencies:
                next_honeycomb_dependencies = dependency.get_dependencies(recursive)

                honeycomb_dependencies |= set(next_honeycomb_dependencies)

        return list(honeycomb_dependencies)
