package com.sgtech.pos.service;

import com.sgtech.pos.dto.ProductDTO;
import com.sgtech.pos.exception.DuplicateResourceException;
import com.sgtech.pos.exception.ResourceNotFoundException;
import com.sgtech.pos.exception.ValidationException;
import com.sgtech.pos.model.Product;
import com.sgtech.pos.repository.ProductRepository;
import org.modelmapper.ModelMapper;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

import java.util.List;
import java.util.stream.Collectors;

public interface ProductService {
    ProductDTO createProduct(ProductDTO productDTO);
    ProductDTO updateProduct(Long id, ProductDTO productDTO);
    List<ProductDTO> getAllProducts();
    ProductDTO getProductById(Long id);
    void deleteProduct(Long id);
    List<ProductDTO> searchProducts(String keyword);
    ProductDTO updateStock(Long id, int quantity);
}

@Service
@Transactional
public class ProductServiceImpl implements ProductService {

    @Autowired
    private ProductRepository productRepository;

    @Autowired
    private ModelMapper modelMapper;

    @Override
    public ProductDTO createProduct(ProductDTO productDTO) {
        // Business validation
        if (productDTO.getPrice() <= 0) {
            throw new ValidationException("Price must be positive");
        }

        // Check duplicates
        if (productRepository.existsByName(productDTO.getName())) {
            throw new DuplicateResourceException("Product already exists");
        }

        Product product = modelMapper.map(productDTO, Product.class);
        Product savedProduct = productRepository.save(product);

        return modelMapper.map(savedProduct, ProductDTO.class);
    }

    @Override
    public ProductDTO updateProduct(Long id, ProductDTO productDTO) {
        Product existingProduct = productRepository.findById(id)
            .orElseThrow(() -> new ResourceNotFoundException("Product not found"));

        // Business validation
        if (productDTO.getPrice() <= 0) {
            throw new ValidationException("Price must be positive");
        }

        // Check duplicates if name changed
        if (!existingProduct.getName().equals(productDTO.getName()) &&
            productRepository.existsByName(productDTO.getName())) {
            throw new DuplicateResourceException("Product name already exists");
        }

        existingProduct.setName(productDTO.getName());
        existingProduct.setPrice(productDTO.getPrice());
        existingProduct.setQuantity(productDTO.getQuantity());

        Product updatedProduct = productRepository.save(existingProduct);

        return modelMapper.map(updatedProduct, ProductDTO.class);
    }

    @Override
    public List<ProductDTO> getAllProducts() {
        List<Product> products = productRepository.findAll();
        return products.stream()
            .map(product -> modelMapper.map(product, ProductDTO.class))
            .collect(Collectors.toList());
    }

    @Override
    public ProductDTO getProductById(Long id) {
        Product product = productRepository.findById(id)
            .orElseThrow(() -> new ResourceNotFoundException("Product not found"));
        return modelMapper.map(product, ProductDTO.class);
    }

    @Override
    public void deleteProduct(Long id) {
        if (!productRepository.existsById(id)) {
            throw new ResourceNotFoundException("Product not found");
        }
        productRepository.deleteById(id);
    }

    @Override
    public List<ProductDTO> searchProducts(String keyword) {
        List<Product> products = productRepository.findByNameContainingIgnoreCase(keyword);
        return products.stream()
            .map(product -> modelMapper.map(product, ProductDTO.class))
            .collect(Collectors.toList());
    }

    @Override
    public ProductDTO updateStock(Long id, int quantity) {
        Product product = productRepository.findById(id)
            .orElseThrow(() -> new ResourceNotFoundException("Product not found"));

        if (product.getQuantity() + quantity < 0) {
            throw new ValidationException("Insufficient stock");
        }

        product.setQuantity(product.getQuantity() + quantity);
        Product updatedProduct = productRepository.save(product);

        return modelMapper.map(updatedProduct, ProductDTO.class);
    }
}
