# Copyright (C) 2019  Collin Capano
# This program is free software; you can redistribute it and/or modify it
# under the terms of the GNU General Public License as published by the
# Free Software Foundation; either version 3 of the License, or (at your
# option) any later version.
#
# This program is distributed in the hope that it will be useful, but
# WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU General
# Public License for more details.
#
# You should have received a copy of the GNU General Public License along
# with this program; if not, write to the Free Software Foundation, Inc.,
# 51 Franklin Street, Fifth Floor, Boston, MA  02110-1301, USA.

from __future__ import absolute_import

import itertools

from .base import BaseProposal


class JointProposal(BaseProposal):
    """A collection of jump proposals for multiple parameters.

    Parameters
    ----------
    proposals : list
        List of pr
    """
    name = 'joint'

    def __init__(self, proposals, random_state=None):
        self.parameters = list(itertools.chain(*[prop.parameters
                                                 for prop in proposals])
        # check that we don't have multiple proposals for the same parameter
        if len(set(self.parameters)) != len(self.parameters):
            # get the repeated parameters
            repeated = [p for p in self.parameters
                        if self.parameters.count(p) > 1]
            raise ValueError("multiple proposals provided for parameter(s) {}"
                             .format(', '.join(repeated)))
        self.symmetric = all(prop.symmetric for prop in proposals)
        if not isinstance(random_state, numpy.random.RandomState):
            random_state = numpy.random.RandomState(random_state)
        self.random_state = random_state
        # have all of the proposals use the same random state
        for prop in self.proposals:
            prop.random_state = random_state
        # store the proposals as a dict of parameters -> proposal; we can do
        # this since the mapping of parameters to proposals is one/many:one
        self.proposals = {prop.params: prop for prop in proposals

    def logpdf(self, vals):
        return sum(p.logpdf(**vals) for p in self.proposals.values())

    def update(self, chain):
        # update each of the proposals
        for prop in self.propsals.values():
            prop.update(chain)

    def jump(self, size=1):
        out = {}
        for prop in proposals:
            out.update(prop.jump(size=size))
        return out

    @property
    def state(self):
        # get all of the proposals state
        state = {params: prop.state for params, prop in self.proposals.items()}
        state = {}
        for params, prop in self.proposals.items():
            s = prop.state
            # remove the random state, as it will be the same as this class's
            # state, which we will set below 
            s.pop('random_state', None)
            if s:
                state[params] = state
        # add the global random state
        state['random_state'] = self.random_state.get_state()
        return state

    def set_state(self, state):
        # set each proposals' state
        for params, prop in self.proposals.items():
            # if a proposal only needs the random state set, then there won't
            # be anything to set for it
            if params in state:
                prop.set_state(state[params])
        # set the state of the random number generator
        self.random_state.set_state(state['random_state'])