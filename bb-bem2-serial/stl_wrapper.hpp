﻿#ifndef STL_WRAPPER_HPP
#define STL_WRAPPER_HPP

#include <span>
#include <memory>
#include <string_view>

#include "stl_loader.h"

inline namespace stl_wrapper
{
    class STLModel {
    public:
        STLModel() = default;

        STLModel(std::string_view filename);

        bool isValid() const;

        std::span<const stl_facet_t> facets() const;

    private:
        struct Impl;
        std::shared_ptr<Impl> p_impl{};
    };
}

#endif // STL_WRAPPER_HPP
